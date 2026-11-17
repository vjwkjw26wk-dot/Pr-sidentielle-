"""M12 — Incertitude des résultats du modèle bouclé (Monte-Carlo), version 0.1.

Sources d'incertitude tirées à chaque simulation :
1. Paramètres estimés : coefficients des équations de comportement (emploi, prix, investissement des branches et des
   sociétés, salaires, consommation, importations, exportations, transmission des prix d'importation), tirés dans une loi
   normale centrée sur l'estimation, avec la matrice de variance-covariance estimée (robuste). Les effets fixes et
   constantes sont recalés après chaque tirage (comme dans le modèle central).
2. Paramètres calibrés, tirés uniformément dans leur plage documentée :
   - élasticité de l'emploi au coût réel du travail : 0,2 à 0,6 ;
   - effet du chômage sur les salaires : −0,8 % à −0,2 % par point ;
   - fermeture d'offre ρ : 0,1 à 0,25 (amortissement fixe 0,3).
Résultat : pour chaque variante, médiane et intervalle à 90 % (5e-95e centiles) des écarts au compte central.
L'incertitude sur les données, la spécification des équations et les hypothèses exogènes n'est pas couverte.
"""
from __future__ import annotations

import copy

import numpy as np
import pandas as pd

import m7_equations as E
import m8_modele as M8

EQUATIONS_TIREES = ("emploi", "prix_va", "investissement", "investissement_snf", "salaires", "consommation",
                    "importations", "exportations", "transmission")


def tirer(mod, rng, origine):
    """Modifie `mod` en place : paramètres tirés ; renvoie les paramètres calibrés tirés."""
    for k in EQUATIONS_TIREES:
        e = mod.eq[k]
        p0, V = origine[k]
        garde = [c for c in p0.index if not c.startswith(("fe_", "tr_"))]
        Vg = V.loc[garde, garde].to_numpy()
        Vg = (Vg + Vg.T) / 2
        try:
            x = rng.multivariate_normal(p0[garde].to_numpy(), Vg, check_valid="ignore")
        except np.linalg.LinAlgError:
            x = p0[garde].to_numpy()
        p = p0.copy()
        p[garde] = x
        e.res.params = p
    r = mod.eq["investissement_snf"].res.params
    mod.eq["investissement_snf"].lr["long terme : élasticité au coût d'usage du capital"] = -r["lcu_1"] / r["ecm_1"]
    t = mod.eq["transmission"].res.params
    mod.theta = float(np.clip(t["dlpm"] / (t["dlpm"] + t["dlpm_1"]), 0.2, 1.0)) if (t["dlpm"] + t["dlpm_1"]) > 0 else 1.0
    cal = {"sigma": rng.uniform(0.2, 0.6), "phillips": rng.uniform(-0.008, -0.002), "rho": rng.uniform(0.1, 0.25)}
    E.SIGMA_TRAVAIL = cal["sigma"]
    E.PHILLIPS = cal["phillips"]
    mod._caler()
    return cal


def monte_carlo(mod, ans, variantes: dict, n=40, graine=12, horizons=(2024, 2026, 2030)) -> pd.DataFrame:
    """variantes : {nom: fonction(mod, ans, rho) -> Exogenes, ou (fonction variante, fonction référence)}. Renvoie un tableau long des écarts par tirage."""
    rng = np.random.default_rng(graine)
    origine = {k: (mod.eq[k].res.params.copy(), mod.eq[k].res.cov_params()) for k in EQUATIONS_TIREES}
    sauve = (E.SIGMA_TRAVAIL, E.PHILLIPS, mod.theta, copy.deepcopy(mod.eq["investissement_snf"].lr))
    lignes = []
    try:
        for i in range(n + 1):
            if i == 0:
                cal = {"sigma": sauve[0], "phillips": sauve[1], "rho": M8.RHO_DEFAUT}   # tirage 0 = modèle central
            else:
                cal = tirer(mod, rng, origine)
            c0 = mod.simuler(ans, M8.exogenes_projection(mod, ans, fermeture_offre=cal["rho"]))
            for nom, f in variantes.items():
                # une variante peut fournir son propre compte de référence : (fonction variante, fonction référence)
                if isinstance(f, tuple):
                    f, fr = f
                    c = mod.simuler(ans, fr(mod, ans, cal["rho"]))
                else:
                    c = c0
                v = mod.simuler(ans, f(mod, ans, cal["rho"]))
                for t in horizons:
                    lignes.append(dict(tirage=i, variante=nom, annee=t, pib=(v.pib[t] / c.pib[t] - 1) * 100,
                                       emploi=v.emploi[t] - c.emploi[t], prix=(v.pc[t] / c.pc[t] - 1) * 100,
                                       solde=v.solde_pib[t] - c.solde_pib[t], dette=v.dette_pib[t] - c.dette_pib[t], **cal))
    finally:
        for k in EQUATIONS_TIREES:
            mod.eq[k].res.params = origine[k][0]
        E.SIGMA_TRAVAIL, E.PHILLIPS, mod.theta = sauve[0], sauve[1], sauve[2]
        mod.eq["investissement_snf"].lr = sauve[3]
        mod._caler()
    return pd.DataFrame(lignes)


def resume(df: pd.DataFrame) -> pd.DataFrame:
    """Valeur centrale (tirage 0), médiane et intervalle à 90 % des tirages."""
    tir = df[df.tirage > 0]
    q = tir.groupby(["variante", "annee"])[["pib", "emploi", "prix", "solde", "dette"]].quantile([0.05, 0.5, 0.95]).unstack()
    c = df[df.tirage == 0].set_index(["variante", "annee"])[["pib", "emploi", "prix", "solde", "dette"]]
    return c, q
