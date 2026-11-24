"""M21 — Compte des sociétés (phase 4.3, chantier B).

Données : Eurostat nasa_10_nf_tr (comptes non financiers par secteur, France, M€ courants, 1995-2025) et nasa_10_f_bs
(bilans financiers consolidés, S11). Aucune série n'est complétée ou extrapolée : les années manquantes restent NaN.

Contenu :
- `donnees()` : panel annuel du compte des sociétés non financières (S11), des revenus de la propriété des ménages
  (S14_S15) et du reste du monde (S2), dette consolidée F3+F4 de S11, taux de marché ;
- `estimer()` : comportements (1996-2019, hors 2020-2021) :
    * dividendes nets versés par S11 : correction d'erreur de type Lintner sur le résultat courant après intérêts et IS
      de l'ANNÉE PRÉCÉDENTE (en France, les dividendes versés en t rémunèrent l'exercice t − 1) ;
    * taux apparent de la dette de S11 : rattrapage partiel du taux de marché (taux à 10 ans + écart constant) ;
    * IS de S11 : taux apparent sur le résultat courant avant impôt (EBE − intérêts nets), proportionnel au taux légal ;
    * part de la variation de la capacité de financement couverte par l'endettement (instruments F3 + F4) ;
- `CompteSocietes` : compte simulé, appelé par M8 quand SPEC["societes"] == "compte".

Statut des paramètres : [E] estimé, [C] calibré sur l'année de base (part, ratio), [H] hypothèse documentée.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
RAW = RACINE / "data" / "raw"


def _js(nom):
    from telechargement import jsonstat_dict
    return pd.Series(jsonstat_dict(json.loads((RAW / nom).read_text())))


def donnees() -> pd.DataFrame:
    s = _js("eurostat_nasa_10_nf_tr_secteurs_FR.json")
    ans = range(1995, 2026)

    def g(d, it, sec, t):
        return float(s.get((d, it, sec, str(t)), np.nan))

    def solde(it, sec, t, signe_recu=1.0):
        """reçu − versé (NaN reste NaN)."""
        return g("RECV", it, sec, t) - g("PAID", it, sec, t)

    rows = {}
    for t in ans:
        r = {}
        # S11 : sociétés non financières
        r["va"] = g("PAID", "B1G", "S11", t) if not np.isnan(g("PAID", "B1G", "S11", t)) else g("RECV", "B1G", "S11", t)
        r["ebe"] = g("RECV", "B2A3G", "S11", t) if not np.isnan(g("RECV", "B2A3G", "S11", t)) else g("PAID", "B2A3G", "S11", t)
        r["int_verses"], r["int_recus"] = g("PAID", "D41", "S11", t), g("RECV", "D41", "S11", t)
        r["int_nets"] = r["int_verses"] - r["int_recus"]
        r["div_verses"], r["div_recus"] = g("PAID", "D42", "S11", t), g("RECV", "D42", "S11", t)
        r["div_nets"] = r["div_verses"] - r["div_recus"]
        r["d43_nets"] = g("PAID", "D43", "S11", t) - g("RECV", "D43", "S11", t)
        r["d44_45_nets"] = (np.nansum([g("RECV", "D44", "S11", t), g("RECV", "D45", "S11", t)])
                            - np.nansum([g("PAID", "D44", "S11", t), g("PAID", "D45", "S11", t)]))
        r["is_"] = g("PAID", "D5", "S11", t)
        r["b8g"] = g("RECV", "B8G", "S11", t) if not np.isnan(g("RECV", "B8G", "S11", t)) else g("PAID", "B8G", "S11", t)
        r["fbcf"] = g("PAID", "P51G", "S11", t)
        r["b9"] = g("RECV", "B9", "S11", t) if not np.isnan(g("RECV", "B9", "S11", t)) else g("PAID", "B9", "S11", t)
        # autres opérations courantes (D6, D7, D8 nets) : solde de l'identité de l'épargne
        r["autres_courants"] = r["b8g"] - (r["ebe"] - r["int_nets"] - r["div_nets"] - r["d43_nets"] + r["d44_45_nets"] - r["is_"])
        # autres emplois en capital (stocks, transferts en capital, acquisitions nettes d'actifs non produits)
        r["autres_capital"] = r["b8g"] - r["fbcf"] - r["b9"]
        # S12 : IS des sociétés financières
        r["is_s12"] = g("PAID", "D5", "S12", t)
        # ménages (S14_S15) : revenus de la propriété
        r["men_d41_nets"] = g("RECV", "D41", "S14_S15", t) - g("PAID", "D41", "S14_S15", t)
        r["men_d42_recus"] = g("RECV", "D42", "S14_S15", t)
        r["men_d4_nets"] = g("RECV", "D4", "S14_S15", t) - g("PAID", "D4", "S14_S15", t)
        # reste du monde : dividendes reçus (versés par les résidents)
        r["s2_d42_recus"] = g("RECV", "D42", "S2", t)
        r["s2_d42_verses"] = g("PAID", "D42", "S2", t)
        r["s12_d42_verses"] = g("PAID", "D42", "S12", t)
        r["s13_d42_recus"] = g("RECV", "D42", "S13", t)
        rows[t] = r
    d = pd.DataFrame(rows).T
    # dette consolidée de S11 (titres de dette + crédits), fin d'année
    b = _js("eurostat_nasa_10_f_bs_S11_CO_FR.json")
    d["dette"] = [float(b.get(("LIAB", "F3", str(t)), np.nan)) + float(b.get(("LIAB", "F4", str(t)), np.nan)) for t in ans]
    d["actifs_liquides"] = [sum(float(b.get(("ASS", f, str(t)), np.nan)) for f in ("F2", "F3", "F4")) for t in ans]
    from m17_dette import taux_observes
    lt, st = taux_observes()
    d["taux_long"] = lt.reindex(d.index)
    d["taux_court"] = st.reindex(d.index)
    # dividendes distribués aux détenteurs finals (ménages, reste du monde, APU) par l'ensemble des sociétés résidentes :
    # flux net des distributions croisées entre sociétés, bien plus régulier que le solde versé − reçu de S11 (écart-type
    # de la variation du taux de distribution 0,12 contre 0,25), et seul flux pertinent pour les revenus des ménages
    d["div_final"] = d.men_d42_recus + d.s2_d42_recus + d.s13_d42_recus
    d["profit"] = d.ebe - d.int_nets - d.is_          # résultat courant après intérêts et IS (base des dividendes)
    d["taux_app"] = 100 * d.int_verses / d.dette.shift(1)
    d["taux_is_app"] = 100 * d.is_ / (d.ebe - d.int_nets)
    d["taux_recu"] = 100 * d.int_recus / d.actifs_liquides.shift(1)
    return d


EXCLUS = (2020, 2021)


def _ols(y, X):
    import statsmodels.api as sm
    m = sm.OLS(y, sm.add_constant(X), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    return m


def estimer(d: pd.DataFrame | None = None, debut=1997, fin=2019, fin_taux=2024) -> dict:
    """Comportements du compte des sociétés. Renvoie les paramètres et les régressions (statsmodels).
    Les équations de taux d'intérêt sont estimées jusqu'en `fin_taux` (2024) : 2022-2024 est le seul épisode de hausse des
    taux de l'échantillon (l'estimation arrêtée en 2019, sur une période de baisse continue, donne un renouvellement presque
    complet en un an, μ = 0,83, contredit en 2023-2024 : +2,1 pt d'erreur hors échantillon)."""
    d = donnees() if d is None else d
    an = [t for t in range(debut, fin + 1) if t not in EXCLUS]
    out = {}
    # 1. dividendes (Lintner, ECM sur le résultat de l'année précédente) ; indicatrices des réformes de la fiscalité des
    #    dividendes : contribution additionnelle de 3 % sur les montants distribués (2013-2017) et prélèvement forfaitaire
    #    unique (à partir de 2018). Elles deviennent des leviers exogènes (Exogenes.fiscalite_dividendes).
    ld, lp = np.log(d.div_final), np.log(d.profit)
    X = pd.DataFrame({"dlp_1": lp.diff().shift(1), "ecart_1": (ld - lp.shift(1)).shift(1)}, index=d.index)
    y = ld.diff()
    out["dividendes_sans_fiscalite"] = _ols(y.loc[an], X.loc[an])
    X2 = X.copy()
    if fin >= 2018:
        X2["pfu"] = (d.index >= 2018).astype(float)
    if fin >= 2013:
        X2["c3"] = ((d.index >= 2013) & (d.index <= 2017)).astype(float)
    out["dividendes_lintner"] = _ols(y.loc[an], X2.loc[an])
    # retenu : taux de distribution du résultat de l'exercice précédent, en niveau (log), avec tendance et indicatrices
    # fiscales. La correction d'erreur de Lintner n'est pas identifiée (λ = −0,09 ± 0,06 : le taux de distribution a
    # doublé entre 1997 et 2019, sans cible stable) et prédit moins bien hors échantillon que la règle proportionnelle.
    lr = ld - lp.shift(1)
    Xn = pd.DataFrame({"tendance": d.index - 2000.0}, index=d.index)
    for k in ("pfu", "c3"):
        if k in X2:
            Xn[k] = X2[k]
    out["dividendes_niveau_tendance"] = _ols(lr.loc[an], Xn.loc[an])
    # 2. taux apparent de la dette (intérêts versés après SIFIM / dette F3+F4 de fin d'année précédente) :
    #    Δr_app = a + β_c r_court + β_l r_10ans − μ r_app_{t−1}. Le taux court domine (crédits à taux variable ou
    #    révisable ; spécification avec le seul taux à 10 ans rejetée : R² 0,51, erreurs hors échantillon de −1 à −1,9 pt).
    an_r = [t for t in range(max(debut, 1999), fin_taux + 1) if t not in EXCLUS]
    for cle, serie, suf in (("taux_apparent", d.taux_app, ""), ("taux_recu", d.taux_recu, "_recu")):
        Xr = pd.DataFrame({"r_court": d.taux_court, "r_long": d.taux_long, "r_app_1": serie.shift(1)}, index=d.index)
        m_r = _ols(serie.diff().loc[an_r], Xr.loc[an_r])
        out[cle] = m_r
        p = m_r.params
        out["mu" + suf] = float(-p["r_app_1"])
        out["poids_court" + suf] = float(p["r_court"] / (p["r_court"] + p["r_long"]))
        out["transmission" + suf] = float((p["r_court"] + p["r_long"]) / out["mu" + suf])
        out["ecart_taux" + suf] = float(p["const"] / out["mu" + suf])
    # IS : élasticité du taux apparent (IS / résultat courant avant impôt) au taux légal, 1997-fin. Non significative
    # (−0,10 ± 0,29) : les baisses de taux (33,3 → 25 %) se sont accompagnées d'élargissements d'assiette.
    import m7_series as S7
    tau = S7.taux_is().reindex(d.index)
    an_i = [t for t in range(debut, fin + 1) if t not in EXCLUS]
    out["is_elasticite"] = _ols(np.log(d.taux_is_app.loc[an_i]), np.log(tau.loc[an_i]).rename("ln_tau"))
    # 3. couverture de la variation du besoin de financement par l'endettement : Δdette = a + φ (−B9) (en % du PIB S11)
    Xd = pd.DataFrame({"besoin": -d.b9 / d.va}, index=d.index)
    m_d = _ols((d.dette.diff() / d.va).loc[an], Xd.loc[an])
    out["dette"] = m_d
    # 4. IS : taux apparent rapporté au résultat avant impôt
    out["taux_is_app"] = d.taux_is_app
    return out


def rapport_estimation(est: dict) -> str:
    lignes = []
    for k in ("dividendes_sans_fiscalite", "dividendes_lintner", "dividendes_niveau_tendance", "taux_apparent", "taux_recu", "dette", "is_elasticite"):
        if k not in est:
            continue
        m = est[k]
        lignes.append(f"[{k}] n={int(m.nobs)} R²={m.rsquared:.2f}")
        for nom in m.params.index:
            lignes.append(f"   {nom:10s} {m.params[nom]:+.3f} (± {m.bse[nom]:.3f})")
    lignes.append(f"μ (rattrapage du taux apparent) = {est['mu']:.3f} ; poids du taux court {est['poids_court']:.2f} ; "
                  f"transmission de long terme {est['transmission']:.2f} ; écart constant {est['ecart_taux']:.2f} pt")
    lignes.append(f"[rejeté] taux reçu sur les actifs liquides : μ = {est['mu_recu']:.3f} ; poids du taux court {est['poids_court_recu']:.2f} ; "
                  f"transmission {est['transmission_recu']:.2f} ; écart {est['ecart_taux_recu']:.2f} pt")
    return "\n".join(lignes)


# ---------------------------------------------------------------------------------------------------------------------
# Paramètres retenus (voir phase43/b2_estimation.py et phase43/NOTE_B.md). Remplis par `parametres()`.
# Les valeurs non identifiées sont calibrées avec variantes (VARIANTES).
VARIANTES = {
    # part de la capacité/besoin de financement supplémentaire couverte par l'endettement (le reste : fonds propres,
    # actifs liquides) ; estimée de façon fragile, calibrée avec variantes
    "phi_dette": {"central": None, "bas": 0.5, "haut": 1.5},      # None : valeur estimée (1,06 ± 0,31 sur 1997-2019)
    # vitesse de rattrapage du taux apparent (si l'estimation est fragile, variantes autour de la valeur estimée)
    "mu_taux": {"central": None, "bas": 0.35, "haut": 0.83},      # central : estimé 1999-2024 ; haut : estimé 1999-2019
    # lissage des dividendes (vitesse d'ajustement au taux de distribution cible, Lintner) : non identifié ; central =
    # 1 (distribution proportionnelle au résultat de t − 1), variante 0,3 (ordre de grandeur de Lintner 1956)
    "div_lissage": {"central": 1.0, "bas": 0.3, "haut": None},
}


_CACHE = {}


def parametres(variante: dict | None = None) -> dict:
    """Paramètres du compte des sociétés : estimés sur 1997-2019 (dividendes, taux), calibrés sinon."""
    if "est" not in _CACHE:
        d = donnees()
        _CACHE["d"], _CACHE["est"] = d, estimer(d)
    d, est = _CACHE["d"], _CACHE["est"]
    v = variante or {}
    choisir = lambda k, val: val if v.get(k, VARIANTES[k]["central"]) is None else float(v.get(k, VARIANTES[k]["central"]))  # noqa: E731
    return {
        "div_lissage": choisir("div_lissage", 1.0),
        # effets des réformes de la fiscalité des dividendes : non identifiés de façon robuste (signe opposé selon la
        # spécification : PFU +0,08 en croissance dans l'équation de Lintner, −0,44 en niveau avec tendance) ; nuls en
        # central, variante « fiscalite » = effets de court terme de l'équation de Lintner, en niveau
        "div_pfu": float(est["dividendes_lintner"].params.get("pfu", 0.0)) if v.get("fiscalite_dividendes") else 0.0,
        "div_c3": float(est["dividendes_lintner"].params.get("c3", 0.0)) if v.get("fiscalite_dividendes") else 0.0,
        "mu_taux": choisir("mu_taux", est["mu"]), "poids_court": est["poids_court"], "transmission": est["transmission"],
        "ecart_taux": est["ecart_taux"],
        "phi_dette": choisir("phi_dette", float(est["dette"].params["besoin"])),
        "donnees": d,
    }


class CompteSocietes:
    """Compte simulé des sociétés non financières (S11) et revenus de la propriété distribués.

    Identités (M€ courants), pour t > B :
      EBE_t        = EBE_B × EBE_marchand_t / EBE_marchand_B                       (champ S11 ⊂ branches marchandes)
      intérêts_t   = (1 − ρ_reçus) r_app_t × dette_{t−1},  ρ_reçus = intérêts reçus / versés de l'année de base [C]
      r_app_t      = r_app_{t−1} + μ (τ (ω r3m_t + (1 − ω) r10_t) + s − r_app_{t−1})   [E, 1999-2024]
      IS_t         = IS_B × (EBE_t − int_t) / (EBE_B − int_B) × f_t,  f_t = τ_t/τ_B × transfert de bénéfices (mesure)
                     ou taux apparent observé / taux apparent de base (rétrosimulation conditionnelle)
      Π_t          = EBE_t − int_t − IS_t   (+ profits induits par les mesures, M14)
      div_t        = div_{t−1} × (ρ_t Π_{t−1} / div_{t−1})^ℓ,  ρ_t = ρ_B exp(γ·Δfiscalité)   [ρ_B C, γ E, ℓ = 1 H]
      div_S11_t    = κ div_t   [C]
      D43, D44-45, autres opérations courantes : ratio à la VA de S11 de l'année de base [C]
      B8G_t        = EBE − int − div − D43 + D44-45 − IS + autres courants
      B9_t         = B8G − FBCF_S11 − autres emplois en capital (ratio à la VA de base) [C]
      dette_t      = dette_B × PIBn_idx_t + φ × Σ_{s≤t} (−(B9_s − B9_B × PIBn_idx_s))   [H : φ, ratio dette/PIB stable en
                     l'absence de choc sur le besoin de financement]
    Dividendes : flux distribué aux détenteurs finals (ménages, reste du monde, APU) par l'ensemble des sociétés
    résidentes, rapporté au résultat de S11 ; répartition entre détenteurs fixe (année de base) ; S11 en supporte une part
    nette fixe κ (le reste : S12 et distributions croisées). S12 n'a pas de comportement propre (NOTE_B_preparation).
    """

    def __init__(self, B: int, variante: dict | None = None):
        p = parametres(variante)
        self.p, self.B = p, B
        d = p["donnees"]
        self.d = d
        b = d.loc[B]
        self.b = b
        self.ratio_va = {k: float(b[k] / b.va) for k in ("d43_nets", "d44_45_nets", "autres_courants", "autres_capital")}
        # répartition des dividendes distribués aux détenteurs finals (année de base) et part nette à la charge de S11
        self.part_men = float(b.men_d42_recus / b.div_final)
        self.part_rdm = float(b.s2_d42_recus / b.div_final)
        self.kappa_s11 = float(b.div_nets / b.div_final)
        self.etat = {}
        # en l'absence de taux court exogène (projection) : écart taux long − taux court de l'année de base
        self.ecart_court_long = float(d.taux_long[B] - d.taux_court[B])
        self.rho_B = float(d.div_final[B] / d.profit[B - 1])
        self.ratio_recus = float(d.int_recus[B] / d.int_verses[B])

    def initialiser(self, A_hist: dict | None = None):
        B, d = self.B, self.d
        e = {"div": {t: float(d.div_final[t]) for t in range(B - 3, B + 1)},
             "profit": {t: float(d.profit[t]) for t in range(B - 3, B + 1)},
             "dette": {B: float(d.dette[B])}, "r_app": {B: float(d.int_verses[B] / d.dette[B - 1])},
             "b9_cumul": 0.0}
        self.etat = e
        return e

    def dividendes(self, t: int, fiscalite: dict | None = None) -> float:
        """Dividendes distribués aux détenteurs finals en t (dépend de l'exercice t − 1 : connu avant la résolution de
        l'année t)."""
        e, p = self.etat, self.p
        if t in e["div"]:
            return e["div"][t]
        pi1 = e["profit"][t - 1]
        d1 = e["div"][t - 1]
        f = fiscalite or {}
        D = lambda a: (f.get(("pfu", a), 1.0 if a >= 2018 else 0.0), f.get(("c3", a), 1.0 if 2013 <= a <= 2017 else 0.0))  # noqa: E731
        (pfu, c3), (pfuB, c3B) = D(t), D(self.B)
        # taux de distribution cible = taux de l'année de base (résultat de B − 1) × effet des réformes fiscales (estimé)
        rho = self.rho_B * np.exp(p["div_pfu"] * (pfu - pfuB) + p["div_c3"] * (c3 - c3B))
        cible = rho * pi1
        dl = p["div_lissage"] * (np.log(cible) - np.log(d1))
        e["div"][t] = d1 * float(np.exp(dl))
        return e["div"][t]

    def dividendes_menages(self, t: int) -> float:
        """Écart des dividendes reçus par les ménages à leur valeur de base indexée sur le PIB nominal : s'ajoute aux
        revenus de la propriété des ménages de M8 (qui, eux, restent indexés pour les intérêts, D44 et D45)."""
        return self.part_men * self.ecart_div(t)

    def ecart_div(self, t, pib_idx=None):
        if pib_idx is None:
            pib_idx = self.etat.get("pib_idx", {}).get(t, self.etat.get("pib_idx", {}).get(t - 1, 1.0))
        return self.etat["div"][t] - float(self.b.div_final) * pib_idx

    def dividendes_rdm(self, t: int) -> float:
        return self.part_rdm * self.ecart_div(t)

    def compte(self, t, ebe_ratio, pib_idx, va_ratio, fbcf_ratio, taux_long, tau_ratio, is_correction=1.0,
               mesure_profits=0.0, taux_court=None, fiscalite=None):
        """Compte de l'année t (appelé après la résolution de l'année). Ratios : valeurs de t rapportées à la base."""
        e, p, b = self.etat, self.p, self.b
        e.setdefault("pib_idx", {})[t] = pib_idx
        va = float(b.va) * va_ratio
        ebe = float(b.ebe) * ebe_ratio
        tc = taux_long - self.ecart_court_long if taux_court is None else taux_court
        r_m = p["transmission"] * (p["poids_court"] * tc + (1 - p["poids_court"]) * taux_long) + p["ecart_taux"]
        r_app = e["r_app"][t - 1] + p["mu_taux"] * (r_m / 100 - e["r_app"][t - 1])
        r_app = max(r_app, 0.0)
        e["r_app"][t] = r_app
        int_v = r_app * e["dette"][t - 1]
        # intérêts reçus : rapport aux intérêts versés de l'année de base [C]. Ce rapport est stable (0,70-0,82 de 2010 à
        # 2025, hors 2021) ; l'équation de taux sur les actifs liquides n'est pas fiable (R² 0,48, transmission 2,8 : les
        # intérêts reçus incluent ceux des prêts aux filiales non résidentes, absents des actifs consolidés), et indexer
        # les actifs sur le PIB sous-estimait les intérêts reçus de 11 à 40 Md€ (b4_compte_isole, variante archivée).
        int_r = self.ratio_recus * int_v
        int_n = int_v - int_r
        rcai0 = float(b.ebe - b.int_nets)
        # IS = taux apparent de base × résultat courant avant impôt × facteur fiscal (rapport des taux légaux × transfert
        # de bénéfices pour une mesure ; taux apparent observé en rétrosimulation conditionnelle)
        is_ = float(b.is_) * max(ebe - int_n, 0.0) / rcai0 * tau_ratio * is_correction
        profit = ebe - int_n - is_ + mesure_profits
        div = self.kappa_s11 * self.dividendes(t, fiscalite)          # dividendes nets à la charge de S11
        e["profit"][t] = profit
        d43 = self.ratio_va["d43_nets"] * va
        d4445 = self.ratio_va["d44_45_nets"] * va
        autres = self.ratio_va["autres_courants"] * va
        b8g = ebe - int_n - div - d43 + d4445 - is_ + autres + mesure_profits
        fbcf = float(b.fbcf) * fbcf_ratio
        b9 = b8g - fbcf - self.ratio_va["autres_capital"] * va
        e["b9_cumul"] += -(b9 - float(b.b9) * pib_idx)
        e["dette"][t] = float(b.dette) * pib_idx + p["phi_dette"] * e["b9_cumul"]

        return dict(ebe_s11=ebe, interets_s11=int_n, interets_verses_s11=int_v, interets_recus_s11=int_r, taux_apparent_s11=100 * r_app, is_s11=is_, profit_s11=profit,
                    dividendes_s11=div, dividendes_distribues=e["div"][t], epargne_s11=b8g, fbcf_s11=fbcf, capacite_s11=b9, dette_s11=e["dette"][t],
                    taux_autofinancement=100 * b8g / fbcf, taux_marge_s11=100 * ebe / va,
                    dividendes_menages_ecart=self.dividendes_menages(t), dividendes_rdm_ecart=self.dividendes_rdm(t),
                    _identite_b8g=b8g - (ebe - int_n - div - d43 + d4445 - is_ + autres + mesure_profits),
                    _identite_b9=b9 - (b8g - fbcf - self.ratio_va["autres_capital"] * va))
