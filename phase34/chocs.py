"""Phase 4.1 : prototype intégré — chocs élémentaires, boucles activées ou gelées, v0.8 et v0.9.

Pour chaque choc et chaque spécification : référence (compte de référence calé, base 2025) et variante. Décomposition :
« tout gelé » (consommation, prix et salaires, emploi, fermeture figés sur la référence : blocs simulés séparément),
puis réactivation d'une boucle à la fois, et modèle complet. Écarts en 2028 (1re année), 2030 et 2035."""
import copy
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "simulateur")]
import m7_equations as E  # noqa: E402
import m8_modele as M8  # noqa: E402
import executer as X  # noqa: E402

CHOCS = {
    "transferts ménages +0,5 pt PIB": [{"type": "transferts_menages", "parametres": {"points_pib": 0.5, "debut": 2028}}],
    "cotisations employeurs −15 Md€": [{"type": "cotisations_employeurs", "parametres": {"md": -15, "debut": 2028}}],
    "investissement public +15 Md€": [{"type": "investissement_public", "parametres": {"md": 15, "debut": 2028}}],
    "IS : taux 25 % → 30 %": [{"type": "taux_is", "parametres": {"taux": 30, "debut": 2028}}],
    "taux d'intérêt +1 pt (courbe)": "oat_haut",
}
BOUCLES = ["C", "prix_salaires", "emploi", "Z"]
ANS_RAPPORT = (2028, 2030, 2035)


def ecarts(mod, c, v, ans):
    out = {}
    for t in ANS_RAPPORT:
        f = lambda k: float(100 * (v[k][t] / c[k][t] - 1))  # noqa: E731
        out[t] = {"PIB": f("pib"), "PIB nominal": f("pib_nominal"), "emploi (milliers)": float(v.emploi[t] - c.emploi[t]),
                  "prix conso": f("pc"), "conso": f("c"), "invest.": f("fbcf"), "salaire": f("salaire"),
                  "recettes (Md€)": float((v.recettes[t] - c.recettes[t]) / 1e3), "dépenses (Md€)": float((v.depenses[t] - c.depenses[t]) / 1e3),
                  "solde (pt PIB)": float(v.solde_pib[t] - c.solde_pib[t]), "dette (pt PIB)": float(v.dette_pib[t] - c.dette_pib[t])}
    return out


def identites(mod, r, ans):
    """Contrôles comptables après choc : dette_t = dette_{t−1} − solde_t (+ calage stock-flux), PIB nominal = volume × prix."""
    err = max(abs(float(r.dette[t] - r.dette[t - 1] + r.solde[t])) for t in ans if t - 1 in r.index)
    return err


def lancer(spec_nom, spec):
    M8.configurer_v08()
    if spec:
        M8.SPEC.update(spec)
        if spec.get("sigma") is not None:
            E.SIGMA_TRAVAIL = spec["sigma"]
    t0 = time.time()
    mod = M8.Modele(2022)
    res = {}
    for nom, mesures in CHOCS.items():
        if isinstance(mesures, str):
            scen_r = {"base": 2022, "horizon": 2035, "mesures": [], "hypotheses": {"europe": False}}
            scen_v = {"base": 2022, "horizon": 2035, "mesures": [], "hypotheses": {"europe": False, "reference": mesures}}
            ref, _, ans, _ = X.construire(scen_r, mod)
            var, _, _, _ = X.construire(scen_v, mod)
        else:
            scen = {"base": 2022, "horizon": 2035, "mesures": mesures, "hypotheses": {"europe": False}}
            ref, var, ans, info = X.construire(scen, mod)
        c = mod.simuler(ans, ref)
        g = mod.trajectoires_gel(ans)
        res[nom] = {}
        for cas, gel in [("tout gelé", BOUCLES)] + [(f"+ {b}", [x for x in BOUCLES if x != b]) for b in BOUCLES] + [("complet", [])]:
            vv = copy.deepcopy(var)
            vv.gel = {k: g[k] for k in gel} or None
            v = mod.simuler(ans, vv)
            res[nom][cas] = ecarts(mod, c, v, ans)
            res[nom][cas]["identite_dette_max_M€"] = identites(mod, v, ans)
        print(f"[{spec_nom}] {nom} : {time.time() - t0:.0f} s", flush=True)
    M8.configurer_v08()
    return res


if __name__ == "__main__":
    specs = {"v0.8": {}, "v0.9": {"demande_travail": "ces_heures", "cible_k": False, "potentiel": "ces_marchand", "sigma": 0.45,
                                   "non_marchand": "branches", "salaire_public": "instrument", "dette": "cohortes",
                                   "cout_travail": "net_subventions"}}
    quoi = sys.argv[1:] or list(specs)
    for s in quoi:
        out = lancer(s, specs[s])
        (pathlib.Path(__file__).parent / "resultats" / f"chocs_{s}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
