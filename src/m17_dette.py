"""M17 — Charge d'intérêts par cohortes d'émission (v0.9, phase 3.4).

Principe
--------
La dette est un portefeuille de titres. Chaque année :
  besoin de financement = déficit + remboursements des titres arrivant à échéance + renouvellement des titres courts ;
  le besoin est couvert par des titres courts (BTF : part de l'encours fixée) et des titres à moyen et long terme émis
  sur une grille de maturités (2 à 50 ans) au taux de la courbe de l'année d'émission ; le coupon est fixe ensuite.
La charge d'intérêts est la somme des coupons des cohortes vivantes et du coût des titres courts.

Ce qui est fixé par des données publiées (AFT, bulletins mensuels 2021-2026, via la recherche documentaire de la
phase 3.3 — à revérifier sur les bulletins originaux, inaccessibles depuis l'environnement de calcul) :
  - durée de vie moyenne de la dette négociable ≈ 8,5 ans depuis 2021 (≈ 7 ans en début de décennie 2010 [à vérifier]) ;
  - part des BTF ≈ 7 % de l'encours ; part des titres indexés ≈ 11 % (émis depuis 1998) : coupon réel = taux nominal de
    la courbe − point mort d'inflation (1,5 point [D]) ; provision d'indexation = inflation de l'année × principal indexé.
Coefficient de passage comptable λ (charge des APU au sens des comptes nationaux / charge reconstituée des titres) :
  estimé sur les 3 années précédant l'origine (information disponible à l'origine), puis constant. Il absorbe les écarts
  de champ (dette non négociable, dépôts, autres administrations), primes et décotes d'émission ; publié comme diagnostic.
Ce qui est conventionnel [D] :
  - grille de maturités à l'émission et poids : déduits de la seule contrainte de durée de vie moyenne (pas d'ajustement
    sur la charge d'intérêts ni sur la règle de l'AFT) ;
  - courbe des taux : interpolation linéaire en log-maturité entre le taux à 3 mois de la zone euro et le taux à 10 ans
    français (Eurostat), plate au-delà de 10 ans ; avant 1994 (pas de taux court), taux court = taux long − 1,5 point ;
  - émissions en milieu d'année : une demi-année de coupon l'année d'émission.
Contrôle externe (non utilisé pour la calibration) : règle de l'AFT (PLF 2026) pour un choc durable de +1 point sur
toute la courbe : +3,2 Md€ à 1 an, +23,5 Md€ à 5 ans, +33,5 Md€ à 9 ans (encours ≈ 2 737 Md€ fin 2025).
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
MATURITES = np.array([2, 3, 5, 7, 10, 15, 20, 30, 50])


def taux_observes():
    """Taux à 10 ans (France) et à 3 mois (zone euro), annuels, en %."""
    from telechargement import jsonstat_dict
    L = lambda f: pd.Series(jsonstat_dict(json.loads((RACINE / "data" / "raw" / f).read_text())))  # noqa: E731
    lt = L("eurostat_irt_lt_mcby_a_FR.json")
    lt = pd.Series({int(t): v for (g, t), v in lt.items() if g == "FR"}).sort_index()
    st = L("eurostat_irt_st_a_EA.json")
    st = pd.Series({int(t): v for t, v in st.items()}).sort_index()
    return lt, st


def courbe(m, court, long_):
    """Taux (%) à la maturité m (années), interpolation linéaire en log-maturité entre 0,25 et 10 ans, plat au-delà."""
    m = np.minimum(np.asarray(m, dtype=float), 10.0)
    x = (np.log(m) - np.log(0.25)) / (np.log(10.0) - np.log(0.25))
    return court + x * (long_ - court)


def poids_emission(duree_cible, part_btf=0.07, duree_btf=0.33):
    """Poids des maturités à l'émission (famille à un paramètre : poids ∝ exp(−λ·m)) tels que la durée de vie moyenne
    de l'encours en régime permanent (émissions constantes) vaille `duree_cible`. Seule contrainte imposée : la durée."""
    def duree(lam):
        w = np.exp(-lam * MATURITES); w /= w.sum()
        # encours en régime permanent : une cohorte de maturité m reste m années, durée résiduelle moyenne (m+1)/2
        enc = w * MATURITES
        d_mlt = float((enc * (MATURITES + 1) / 2).sum() / enc.sum())
        return (1 - part_btf) * d_mlt + part_btf * duree_btf, w
    lo, hi = -0.5, 2.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        d, _w = duree(mid)
        lo, hi = (mid, hi) if d > duree_cible else (lo, mid)
    return duree(0.5 * (lo + hi))[1]


def initialiser_historique(dette, annee, lt, st, debut=1996, duree_cible=7.0, part_btf=0.07, inflation=None,
                           charge_observee=None, recul_lambda=3):
    """Portefeuille de l'année `annee` reconstitué en faisant vivre un portefeuille de régime permanent depuis `debut`
    avec les variations de dette et les taux observés : la structure par millésime reflète l'histoire des émissions
    (forte croissance de la dette 2008-2010 émise à taux bas), sans ajustement de niveau."""
    P = PortefeuilleDette(float(dette[debut]), debut, lt, st, duree_cible=duree_cible, part_btf=part_btf,
                          inflation_hist=inflation)
    ratios = []
    for t in range(debut + 1, annee + 1):
        r = P.avancer(t, float(dette[t] - dette[t - 1]), P._court(t), P._long(t))
        if charge_observee is not None and t > annee - recul_lambda:
            ratios.append(float(charge_observee[t]) / r["charge"])
    if ratios:
        P.lam = float(np.mean(ratios))       # coefficient de passage comptable, information ≤ origine
    P.annee = annee
    return P


class PortefeuilleDette:
    """Portefeuille de dette par cohortes (montants en M€)."""

    def __init__(self, encours, annee, taux_hist_long, taux_hist_court, duree_cible=8.5, part_btf=0.07,
                 charge_observee=None, part_indexee=0.11, point_mort=1.5, inflation_hist=None):
        """Encours initial réparti en régime permanent selon les poids d'émission ; coupons = taux de la courbe de
        l'année d'émission (historique observé). Si `charge_observee` est donnée, l'écart initial entre la charge
        reconstituée et la charge observée est conservé comme ajustement constant (en M€ indexé sur l'encours) et
        publié (`ecart_initial`), sans modifier les coupons."""
        self.part_btf, self.annee = part_btf, annee
        self.part_ix, self.pm, self.infl = part_indexee, point_mort, (inflation_hist if inflation_hist is not None else pd.Series(dtype=float))
        self.lam = 1.0
        self.w = poids_emission(duree_cible, part_btf)
        self.lt, self.st = taux_hist_long, taux_hist_court
        mlt = encours * (1 - part_btf)
        enc_rel = self.w * MATURITES
        flux = mlt / enc_rel.sum()           # émission annuelle de régime permanent
        self.cohortes = []                   # [échéance, principal, coupon %]
        for k, m in enumerate(MATURITES):
            for age in range(int(m)):        # émise il y a `age` années (fin d'année `annee`), échéance dans m − age ans
                a_em = annee - age
                c = float(courbe(m, self._court(a_em), self._long(a_em)))
                ix = self.part_ix if a_em >= 1998 else 0.0
                self.cohortes.append([annee + int(m) - age, flux * self.w[k] * (1 - ix), c, False])
                if ix:
                    self.cohortes.append([annee + int(m) - age, flux * self.w[k] * ix, c - self.pm, True])
        self.btf = encours * part_btf
        self.taux_btf = self._court(annee)
        self.ecart = 0.0
        ch = self.charge_theorique()
        self.ecart_initial = None if charge_observee is None else (charge_observee - ch) / encours
        self.ecart = 0.0 if charge_observee is None else self.ecart_initial

    def _long(self, a):
        return float(self.lt.get(a, self.lt.iloc[0] if a < self.lt.index[0] else self.lt.iloc[-1]))

    def _court(self, a):
        if a in self.st.index:
            return float(self.st[a])
        return self._long(a) - 1.5 if a < self.st.index[0] else float(self.st.iloc[-1])

    def encours(self):
        return sum(c[1] for c in self.cohortes) + self.btf

    def _infl(self, a):
        return float(self.infl.get(a, self.pm)) if len(self.infl) else self.pm

    def _charge_cohortes(self, cohs, annee, facteur=1.0):
        """Coupons (nominaux ou réels) + provision d'indexation des titres indexés (inflation de l'année)."""
        return facteur * sum(c[1] * (c[2] + (self._infl(annee) if c[3] else 0.0)) / 100 for c in cohs)

    def charge_theorique(self, annee=None):
        annee = self.annee if annee is None else annee
        return self._charge_cohortes(self.cohortes, annee) + self.btf * self.taux_btf / 100

    def avancer(self, annee, deficit, court, long_):
        """Fait vivre le portefeuille une année : remboursements, émissions, charge d'intérêts de l'année (M€)."""
        echus = [c for c in self.cohortes if c[0] <= annee]
        rembourse = sum(c[1] for c in echus)
        self.cohortes = [c for c in self.cohortes if c[0] > annee]
        charge_vivantes = self._charge_cohortes(self.cohortes, annee)
        # les titres échus l'année t paient en moyenne une demi-année de coupon
        charge_echus = self._charge_cohortes(echus, annee, 0.5)
        # les titres indexés sont remboursés au principal indexé : la provision accumulée est déjà comptée en charge
        enc_fin = self.encours() + rembourse + deficit        # encours visé en fin d'année (avant renouvellement BTF)
        btf_nouv = self.part_btf * enc_fin
        emission = rembourse + deficit - (btf_nouv - self.btf)
        cour = courbe(MATURITES, court, long_)
        for k, m in enumerate(MATURITES):
            self.cohortes.append([annee + int(m), emission * self.w[k] * (1 - self.part_ix), float(cour[k]), False])
            if self.part_ix:
                self.cohortes.append([annee + int(m), emission * self.w[k] * self.part_ix, float(cour[k]) - self.pm, True])
        charge_nouv = 0.5 * sum(emission * self.w[k] * (float(cour[k]) - self.part_ix * self.pm + self.part_ix * self._infl(annee)) / 100
                                for k in range(len(MATURITES)))
        # BTF (≈ 4 mois) : renouvelés au taux court de l'année
        charge_btf = 0.5 * (self.btf + btf_nouv) * court / 100
        self.btf, self.taux_btf = btf_nouv, court
        enc = self.encours()
        charge = self.lam * (charge_vivantes + charge_echus + charge_nouv + charge_btf) + self.ecart * enc
        return {"charge": charge, "encours": enc, "emission_mlt": emission, "rembourse": rembourse,
                "taux_apparent": 100 * charge / max(enc - deficit, 1.0)}


def regle_aft(annee=2025, encours=2_737_000.0, deficit=140_000.0, court=2.2, long_=3.4, duree_cible=8.5, horizons=(1, 5, 9)):
    """Contrôle externe : écart de charge (Md€) entre un choc durable de +1 point sur toute la courbe et la référence,
    encours et besoin de financement de 2025 (taux maintenus au niveau de 2025)."""
    lt, st = taux_observes()
    res = {}
    for choc in (0.0, 1.0):
        P = PortefeuilleDette(encours, annee, lt, st, duree_cible=duree_cible)
        ch = []
        for h in range(1, max(horizons) + 1):
            ch.append(P.avancer(annee + h, deficit, court + choc, long_ + choc)["charge"])
        res[choc] = ch
    return {h: (res[1.0][h - 1] - res[0.0][h - 1]) / 1000 for h in horizons}


if __name__ == "__main__":
    print("Poids d'émission (durée 8,5 ans) :", dict(zip(MATURITES.tolist(), np.round(poids_emission(8.5), 3).tolist())))
    for d in (7.0, 8.0, 8.5, 9.0):
        r = regle_aft(duree_cible=d)
        print(f"durée de vie {d} ans : choc +1 pt → " + ", ".join(f"{h} an(s) : +{v:.1f} Md€" for h, v in r.items()))
    print("Référence AFT (PLF 2026) : 1 an +3,2 ; 5 ans +23,5 ; 9 ans +33,5 Md€")
