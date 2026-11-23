"""Phase 3.1 — rétrosimulation historique (backtest) du modèle sur 2010-2025.

Principes (calibration et validation séparées)
- Coefficients des équations estimés jusqu'à l'année d'origine seulement (`Modele(B, B)`) : aucune information
  postérieure à l'origine n'entre dans l'estimation.
- PIB potentiel « en temps réel » : productivité globale des facteurs (PGF) implicite filtrée (Hodrick-Prescott,
  λ = 100) sur 1997-origine, prolongée au rythme moyen des huit dernières années ; chômage structurel filtré sur
  1980-origine, maintenu à sa dernière valeur. Le potentiel attendu à l'origine (capital et population active
  prolongés à leur tendance) sert de référence pour le terme d'anticipation.
- Exogènes observées (connues ex post, comme dans toute prévision conditionnelle) : demande et prix mondiaux, prix
  d'importation par produit (dont énergie), consommation publique, investissements autres, population active, taux
  longs, taux d'IS, prestations en volume, autres dépenses publiques en part du PIB, et politiques fiscales sous forme
  de taux apparents (impôts sur les produits, impôts des ménages, cotisations) — les politiques sont des données, pas
  des résultats à valider.
- Variables validées (jamais injectées) : PIB, consommation, investissement, exportations, importations, emploi,
  chômage, productivité, prix, salaires réels, recettes, solde et dette publics.
- La crise sanitaire (2020-2021) n'a pas de mécanisme dans le modèle (confinements, activité partielle) : elle est
  exclue des simulations continues ; une rétrosimulation part de 2021 pour le choc énergétique et inflationniste.

Usage : python3 phase31/backtest.py [variante ...]
Sortie : phase31/resultats/backtest.json
"""
import copy
import json
import pathlib
import sys

import numpy as np
import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]
import m8_modele as M  # noqa: E402
from statsmodels.tsa.filters.hp_filter import hpfilter  # noqa: E402

OUT = R / "phase31" / "resultats"
ORIGINES = {"2010-2019": (2010, 2019), "2012-2019": (2012, 2019), "2014-2019": (2014, 2019), "2016-2019": (2016, 2019),
            "2021-2025": (2021, 2025)}
VARIANTES = {
    # nom : (ρ, a, θ, mode, μ) — même ensemble de politiques observées pour toutes les variantes (taux apparents des
    # recettes) ; v0.6 : fermeture sur le chômage (terme proportionnel 0,3) ; v0.7 : paramètres de la v0.7 ;
    # v0.8 : retenus en phase 3.1 ; variantes de sensibilité
    "demande": (0.0, 0.0, 0.0, "production", 0.0),
    "v06": (0.15, 0.3, 0.0, "chomage", 0.0),
    "v07": (0.15, 0.3, 1.5, "production", 0.3),
    "v08": (0.2, 0.0, 0.75, "production", 0.0),
    "v08_theta05": (0.2, 0.0, 0.5, "production", 0.0),
    "v08_theta10": (0.2, 0.0, 1.0, "production", 0.0),
    "v08_sans_politiques": (0.2, 0.0, 0.75, "production", 0.0),
    "v08_prix_fiscal": (0.2, 0.0, 0.75, "production", 0.0),
    "v08_cout_travail": (0.2, 0.0, 0.75, "production", 0.0),
}


def k_agg(mod, t):
    p = mod.panel
    return float(p[(p.annee == t) & (p.branche.isin(mod.BR))].k.sum()) if hasattr(mod, "BR") else float(p[p.annee == t].k.sum())


def ustar_temps_reel(mod, B):
    u = mod.macro.chomage.loc[1980:B].dropna()
    _, tr = hpfilter(u, lamb=100)
    return float(tr.iloc[-1]), tr


# Baisses du coût du travail (CICE et pacte de responsabilité), Md€ cumulés, ordres de grandeur des créances et des
# allègements (France Stratégie, comité de suivi du CICE, 2020 ; DG Trésor) — politiques observées, entrées exogènes
BAISSES_COUT_TRAVAIL = {2013: 11.0, 2014: 17.0, 2015: 22.5, 2016: 28.0, 2017: 30.0, 2018: 30.0, 2019: 32.0}
PART_SALAIRES_LT = 0.5          # part revenant aux salaires à long terme (valeur centrale de la v0.8)


def construire(B, fin, rho, a, theta, mode, politiques=True, mu=None, cout_travail=False, prix_fiscal=False):
    mod = M.Modele(B, B)
    ans = range(B + 1, fin + 1)
    ex = M.exogenes_observes(mod, ans)
    m, men, apu = mod.macro, mod.men, mod.apu
    # chômage structurel en temps réel
    us, tr = ustar_temps_reel(mod, B)
    ex.chomage_structurel = pd.Series({t: (float(tr.get(t, us)) if t <= B else us) for t in range(1980, fin + 1)})
    # PIB potentiel en temps réel
    alpha = M.ALPHA_K
    BRs = [b for b in mod.H] if hasattr(mod, "H") else None
    pa = ex.population_active
    tfp = {}
    for t in range(1998, B + 1):
        K = sum(float(mod.hist[b].k[t - 1]) for b in mod.hist)
        Ns = float(pa[t]) * (1 - float(ex.chomage_structurel[t]) / 100)
        tfp[t] = np.log(float(m.pib[t])) - alpha * np.log(K) - (1 - alpha) * np.log(Ns)
    tfp = pd.Series(tfp)
    _, tft = hpfilter(tfp, lamb=100)
    g = float((tft.iloc[-1] - tft.iloc[-9]) / 8)
    lpgf = {t: float(tft.get(t, tft.iloc[-1] + g * (t - B))) for t in range(1998, fin + 1)}
    ex.lpgf = pd.Series(lpgf)
    ex.fermeture_mode = mode
    ex.fermeture_offre = rho
    ex.comportements = {"AMORTI_PRODUCTION": a, "AMORTI_FERMETURE": a, "THETA_ANTICIPATION": theta}
    if mu is not None:
        ex.mu_import = mu
    # potentiel attendu à l'origine (anticipation) : capital et population active à leur tendance des 8 dernières années
    K_B = sum(float(mod.hist[b].k[B - 1]) for b in mod.hist)
    K_B8 = sum(float(mod.hist[b].k[B - 9]) for b in mod.hist)
    gk = np.log(K_B / K_B8) / 8
    gpa = np.log(float(pa[B]) / float(pa[B - 8])) / 8
    lpot, lk = {}, {}
    for t in range(B + 1, fin + 1):
        lkt = np.log(K_B) + gk * (t - B)
        lnt = np.log(float(pa[B])) + gpa * (t - B) + np.log(1 - us / 100)
        lk[t] = lkt
        lpot[t] = lpgf[t] + alpha * lkt + (1 - alpha) * lnt
    ex.lpot_ref, ex.lk_ref, ex.ly_ref = pd.Series(lpot), pd.Series(lk), pd.Series(lpot)
    if politiques:
        # politiques fiscales observées, sous forme de taux apparents rapportés à l'année d'origine
        cnom = m.c_cp
        r_prod = apu.d2rec / cnom
        base_men = men.d1 + men.ebe + men.d4 + men.d62
        r_men = men.d5 / base_men
        r_cot = apu.d61rec / men.d1
        pibn = m.pib_cp
        ex.niveaux = {
            "impots_produits": pd.Series({t: float(r_prod[t] / r_prod[B] - 1) for t in ans}),
            **({"prix_conso": pd.Series({t: 0.9 * float(np.log((1 + r_prod[t]) / (1 + r_prod[B]))) for t in ans})} if prix_fiscal else {}),
            "impots_menages_pib": pd.Series({t: float((r_men[t] - r_men[B]) * base_men[t] / pibn[t] * 100) for t in ans}),
        }
        ex.taux_cotisations = pd.Series({t: float(r_cot[t] / r_cot[B]) for t in ans})
    if cout_travail:
        d1 = men.d1
        L = {t: float(np.log1p(-(BAISSES_COUT_TRAVAIL.get(t, 0.0) - BAISSES_COUT_TRAVAIL.get(B, 0.0)) * 1e3 / d1[t])) if t in BAISSES_COUT_TRAVAIL else 0.0
             for t in range(B, fin + 1)}
        for t in range(B + 1, fin + 1):
            if t not in BAISSES_COUT_TRAVAIL and t - 1 in BAISSES_COUT_TRAVAIL:
                L[t] = L[t - 1]
        ex.choc_salaire = pd.Series({t: L[t] - L[t - 1] for t in ans})
        niv = ex.niveaux or {}
        niv["ancre_salaire"] = pd.Series({t: (1 - PART_SALAIRES_LT) * L[t] for t in ans})
        ex.niveaux = niv
    return mod, ex, ans


def observe(mod):
    m, apu = mod.macro, mod.apu
    o = {"pib": m.pib, "c": m.c, "fbcf": m.fbcf, "x": m.x, "m": m.m, "emploi": mod.emp.emploi, "chomage": m.chomage, "pc": m.p_c,
         "solde_pib": (apu.tr - apu.te) / m.pib_cp * 100, "dette_pib": apu.dette / m.pib_cp * 100, "recettes_pib": apu.tr / m.pib_cp * 100,
         "depenses_pib": apu.te / m.pib_cp * 100}
    o["productivite"] = m.pib / mod.emp.emploi
    o["salaire_reel"] = (mod.men.d1 / mod.emp.emploi) / m.p_c
    return o


def simuler(nom, B, fin, rho, a, theta, mode, politiques=True, mu=None, cout_travail=False, prix_fiscal=False):
    mod, ex, ans = construire(B, fin, rho, a, theta, mode, politiques, mu, cout_travail, prix_fiscal)
    r = mod.simuler(ans, ex)
    o = observe(mod)
    sim = {"pib": r.pib, "c": r.c, "fbcf": r.fbcf, "x": r.x, "m": r.m, "emploi": r.emploi, "chomage": r.chomage, "pc": r.pc,
           "solde_pib": r.solde_pib, "dette_pib": r.dette_pib, "recettes_pib": r.recettes / r.pib_nominal * 100,
           "depenses_pib": r.depenses / r.pib_nominal * 100, "productivite": r.pib / r.emploi,
           "salaire_reel": r.salaire / r.pc, "ecart_production": r.ecart_production}
    out = {}
    for k, s in sim.items():
        if k == "ecart_production":
            out[k] = {"sim": {int(t): float(s[t]) for t in ans}}
            continue
        ob = o[k]
        niveau = k in ("chomage", "solde_pib", "dette_pib", "recettes_pib", "depenses_pib")
        if niveau:
            sim_t = {int(t): float(s[t]) for t in ans}
            obs_t = {int(t): float(ob[t]) for t in ans if t in ob.index and not np.isnan(ob[t])}
            err = {t: sim_t[t] - obs_t[t] for t in obs_t}
            out[k] = {"sim": sim_t, "obs": obs_t, "erreur": err, "type": "niveau (points)"}
        else:
            # croissance annuelle simulée et observée ; erreur de niveau cumulée (%)
            base_s = {B: float(ob[B])}
            ss = {**base_s, **{int(t): float(s[t]) for t in ans}}
            if k == "salaire_reel":           # échelles différentes : on raccorde la simulation à l'observé à l'origine
                f = float(ob[B]) / float(s[ans[0]] / (1 + 0.0)) if False else None
                ss = {B: 1.0, **{int(t): float(s[t] / s[ans[0]]) * (float(ob[ans[0]]) / float(ob[B])) for t in ans}}
                obn = {t: float(ob[t] / ob[B]) for t in range(B, fin + 1) if t in ob.index}
            elif k == "productivite":
                ss = {B: 1.0, **{int(t): float(s[t] / (float(mod.macro.pib[B]) / float(mod.emp.emploi[B]))) for t in ans}}
                obn = {t: float(ob[t] / ob[B]) for t in range(B, fin + 1) if t in ob.index}
            else:
                obn = {t: float(ob[t]) for t in range(B, fin + 1) if t in ob.index}
            gs = {t: 100 * (ss[t] / ss[t - 1] - 1) for t in ans}
            go = {t: 100 * (obn[t] / obn[t - 1] - 1) for t in ans if t in obn and t - 1 in obn}
            lev = {t: 100 * (ss[t] / ss[B] / (obn[t] / obn[B]) - 1) for t in ans if t in obn}
            out[k] = {"croissance_sim": gs, "croissance_obs": go, "erreur_niveau_pct": lev, "type": "croissance (%)"}
        e = [v for v in (out[k].get("erreur") or {t: out[k]["croissance_sim"][t] - out[k]["croissance_obs"][t] for t in out[k]["croissance_obs"]}).values()]
        out[k]["rmse"] = float(np.sqrt(np.mean(np.square(e)))) if e else None
        out[k]["biais"] = float(np.mean(e)) if e else None
    # référence naïve : croissance moyenne des cinq années précédant l'origine
    for k in ("pib", "c", "fbcf", "x", "m", "emploi", "pc"):
        ob = o[k]
        moy = np.mean([100 * (ob[t] / ob[t - 1] - 1) for t in range(B - 4, B + 1)])
        e = [moy - out[k]["croissance_obs"][t] for t in out[k]["croissance_obs"]]
        out[k]["rmse_naif"] = float(np.sqrt(np.mean(np.square(e))))
    return out


def main():
    noms = sys.argv[1:] or list(VARIANTES)
    f = OUT / "backtest.json"
    res = json.loads(f.read_text()) if f.exists() else {}
    for nom in noms:
        rho, a, theta, mode, mu = VARIANTES[nom]
        for per, (B, fin) in ORIGINES.items():
            try:
                res[f"{nom}|{per}"] = simuler(nom, B, fin, rho, a, theta, mode, politiques=(nom != "v08_sans_politiques"), mu=mu,
                                               cout_travail=nom.endswith("cout_travail"), prix_fiscal=(nom == "v08_prix_fiscal"))
            except Exception as e:  # noqa: BLE001
                res[f"{nom}|{per}"] = {"erreur": repr(e)}
            r = res[f"{nom}|{per}"]
            if "erreur" in r:
                print(nom, per, r["erreur"][:300])
            else:
                print(nom, per, {k: round(v["rmse"], 2) for k, v in r.items() if v.get("rmse") is not None},
                      "fin : PIB", round(list(r["pib"]["erreur_niveau_pct"].values())[-1], 1), "%, chômage",
                      round(list(r["chomage"]["erreur"].values())[-1], 1), ", dette", round(list(r["dette_pib"]["erreur"].values())[-1], 1), flush=True)
    f.write_text(json.dumps(res, default=float))


if __name__ == "__main__":
    main()
