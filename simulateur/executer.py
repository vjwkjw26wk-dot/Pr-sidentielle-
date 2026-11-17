"""Exécution d'un scénario (version 0.1).

Entrée : un scénario JSON (voir `scenarios/exemple_programme.json`) :
  {"nom", "description", "base": 2022, "horizon": 2030,
   "hypotheses": {"fermeture_offre": 0.15, "europe": true, "incertitude": 0},
   "mesures": [{"type": <clé du catalogue>, "parametres": {...}}, ...]}
Sortie : dictionnaire JSON-sérialisable : trajectoires de référence et du scénario, écarts, effets distributifs
(mesures socio-fiscales), incertitude, et la fiche de transparence (mesures, hypothèses, données, modèles, paramètres
sensibles, incertitudes, limites).
Usage : python3 -m simulateur.executer scenarios/exemple_programme.json [sortie.json]
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "tests"))
import m8_modele as M8  # noqa: E402
from simulateur import catalogue as CAT  # noqa: E402

_MODELES = {}
VARIABLES = {"pib": "PIB en volume (M€ 2015)", "c": "Consommation des ménages", "fbcf": "Investissement", "x": "Exportations",
             "m": "Importations", "emploi": "Emploi (milliers)", "chomage": "Taux de chômage (%)", "pc": "Prix à la consommation (indice)",
             "salaire": "Salaire moyen par tête", "rdb": "Revenu disponible brut (M€)", "solde_pib": "Solde public (% du PIB)",
             "dette_pib": "Dette publique (% du PIB)", "recettes": "Recettes publiques (M€)", "depenses": "Dépenses publiques (M€)",
             "tuc_industrie": "Taux d'utilisation des capacités, industrie (%)"}
EN_POINTS = {"chomage", "solde_pib", "dette_pib", "tuc_industrie"}


def modele(base: int) -> M8.Modele:
    if base not in _MODELES:
        _MODELES[base] = M8.Modele(base)
    return _MODELES[base]


def _serie_g(mod, ex, points, debut):
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    return ex.conso_publique * pd.Series({t: (1 + points / 100 * mod.macro.pib_cp[mod.B] / g_part if t >= debut else 1.0)
                                          for t in ex.conso_publique.index})


def construire(scenario: dict, mod, central=None, journal=None):
    """Exogènes de référence et du scénario, et informations complémentaires (distribution, M9)."""
    H = scenario.get("hypotheses", {})
    ans = range(mod.B + 1, scenario.get("horizon", 2030) + 1)
    rho = H.get("fermeture_offre", M8.RHO_DEFAUT)
    mesures = scenario.get("mesures", [])
    info = {"distribution": None, "statique": {}}
    kw = {"fermeture_offre": rho}
    ages = [m for m in mesures if m["type"] == "age_legal"]
    l9 = None
    if ages or H.get("demographie_m9", True):
        import m9_retraites as R
        act = R.ActiviteSeniors()
        pens = R.Pensions(act)
        k = act.estimer_part_emploi()
        base9 = R.liens_m8(mod, ans, "actuelle", "actuelle", act, pens, k)
        kw["population_active"] = base9["population_active"]
        if ages:
            if central is None:
                central = mod.simuler(ans, M8.exogenes_projection(mod, ans, **kw))
            l9 = R.liens_m8(mod, ans, str(ages[-1]["parametres"]["regle"]), "actuelle", act, pens, k, central=central)
    ref = M8.exogenes_projection(mod, ans, **kw)
    var = M8.exogenes_projection(mod, ans, **kw)
    if l9 is not None:
        var.population_active = l9["population_active"]
        var.ajust_prestations = l9["ajust_prestations"]
        var.emploi_additionnel = l9["emploi_additionnel"]
        info["statique"]["pensions_M€"] = {int(t): float(v) for t, v in l9["ajust_prestations"].items()}
    mm = {"impots": 0.0, "prestations": 0.0, "annee": 2024, "debut": mod.B + 1}
    for m in mesures:
        t, p = m["type"], m.get("parametres", {})
        debut = int(p.get("debut", mod.B + 2))
        if t == "depense_publique":
            var.conso_publique = _serie_g(mod, var, float(p["points_pib"]), debut)
        elif t == "taux_is":
            var.taux_is = pd.Series({a: (M8.S.taux_is().get(a, 25.83) if a < debut else float(p["taux"])) for a in range(2019, max(ans) + 1)})
        elif t == "transferts_menages":
            mm["prestations"] += float(p["points_pib"]) / 100 * mod.macro.pib_cp[mod.B]
            mm["annee"], mm["debut"] = mod.B, debut
        elif t == "energie_import":
            for prod in ("CPA_B", "CPA_C19", "CPA_D"):
                var.prix_import[prod] = [x * (1 + float(p["hausse"]) if a >= debut else 1.0) for a, x in zip(var.prix_import.index, var.prix_import[prod])]
        elif t == "salaires":
            var.choc_salaire = pd.Series({debut: float(np.log1p(float(p["hausse"])))})
        elif t == "reindustrialisation":
            if central is None:
                central = mod.simuler(ans, ref)
            prods = p.get("produits", CAT.INDUSTRIE_DEFAUT)
            var.reindustrialisation = {"produits": {x: 1 - float(p["baisse_parts_importees"]) for x in prods}, "debut": debut,
                                       "duree": int(p.get("duree", 5)), "surcout": float(p.get("surcout", 0.10))}
            var.phi_impose = central.phi
    reforme, calc = CAT.reforme_openfisca(mesures)
    if reforme:
        import m10_couplage as C
        if journal is not None:
            journal.append("microsimulation des ménages (OpenFisca) : quelques minutes")
        base = C.evaluer("base", None)
        nom = "scn_" + hashlib.sha1(json.dumps(reforme, sort_keys=True).encode()).hexdigest()[:10]
        r = C.evaluer(nom, reforme, calculer=calc)
        x = C.mesure_pour_m8(base, r)
        mm["impots"] += x["impots"]
        mm["prestations"] += x["prestations"]
        mm["annee"] = 2024
        D = C.distribution(base, r)
        info["distribution"] = D.reset_index().to_dict(orient="records")
        info["statique"].update({"impot_revenu_M€": x["impots"], "prestations_versees_M€": x["prestations"],
                                 "droits_M€": {v: (r[v] - base[v]) / 1e6 for v in C.PRESTATIONS}})
    if mm["impots"] or mm["prestations"]:
        var.mesure_menages = mm
    return ref, var, ans, info


def executer(scenario: dict) -> dict:
    t0 = time.time()
    journal = []
    mod = modele(scenario.get("base", 2022))
    H = scenario.get("hypotheses", {})
    ref, var, ans, info = construire(scenario, mod, journal=journal)
    if H.get("europe", True):
        import m11_europe as EU
        c, v, E = EU.simuler_couple(mod, ans, ref, var, theta=H.get("prime_risque", EU.THETA_PRIME))
        europe = E.reset_index().rename(columns={"index": "annee"}).to_dict(orient="records")
    else:
        c, v = mod.simuler(ans, ref), mod.simuler(ans, var)
        europe = None
    traj = {}
    for k in VARIABLES:
        traj[k] = {"reference": {int(t): float(c[k][t]) for t in ans}, "scenario": {int(t): float(v[k][t]) for t in ans},
                   "ecart": {int(t): float(v[k][t] - c[k][t] if k in EN_POINTS else (v[k][t] / c[k][t] - 1) * 100) for t in ans},
                   "unite_ecart": "points" if k in EN_POINTS else "%"}
    incert = None
    n = int(H.get("incertitude", 0))
    if n:
        import m12_incertitude as MC
        sc = copy.deepcopy(scenario)

        def f_var(mod_, ans_, rho):
            sc["hypotheses"]["fermeture_offre"] = rho
            return construire(sc, mod_)[1]

        def f_ref(mod_, ans_, rho):
            sc["hypotheses"]["fermeture_offre"] = rho
            return construire(sc, mod_)[0]
        df = MC.monte_carlo(mod, ans, {"scenario": (f_var, f_ref)}, n=n, horizons=tuple(a for a in (ans[1], ans[3] if len(ans) > 3 else ans[-1], ans[-1])))
        tir = df[df.tirage > 0]
        incert = {int(a): {col: [float(g[col].quantile(0.05)), float(g[col].quantile(0.95))] for col in ("pib", "emploi", "prix", "solde", "dette")}
                  for a, g in tir.groupby("annee")}
    profils_res = None
    reforme, _ = CAT.reforme_openfisca(scenario.get("mesures", []))
    if reforme and H.get("profils", True):
        from simulateur import profils
        profils_res = profils.comparer(reforme)
    return {"scenario": scenario, "trajectoires": traj, "distribution": info["distribution"], "statique": info["statique"],
            "profils": profils_res,
            "europe": europe, "incertitude": incert, "transparence": transparence(scenario), "duree_s": round(time.time() - t0),
            "journal": journal}


def transparence(scenario: dict) -> dict:
    """Fiche de transparence exigée par le cahier des charges (§ 17.1)."""
    mes = []
    modules = {"M8", "M1"}
    for m in scenario.get("mesures", []):
        c = CAT.MESURES[m["type"]]
        modules.update(c["modules"])
        mes.append({"type": m["type"], "libelle": c["libelle"], "parametres": m.get("parametres", {}), "niveau_de_preuve": c["preuve"], "limites": c["limites"]})
    H = scenario.get("hypotheses", {})
    if H.get("europe", True):
        modules.add("M11")
    return {
        "mesures": mes,
        "hypotheses": {
            "compte_de_reference": "Compte central conventionnel, et non une prévision : demande mondiale +3 %/an, prix mondiaux et d'importation +1,5 %/an, "
                                   "consommation publique et autres investissements +1 %/an en volume, chômage structurel 7,5 %, taux long 3,2 %, "
                                   "législation inchangée, population active de M9 (législation des retraites actuelle).",
            "fermeture_offre": H.get("fermeture_offre", M8.RHO_DEFAUT),
            "europe": H.get("europe", True),
            "productivite": "tendances de branche des 8 dernières années observées"},
        "donnees": "Insee, Eurostat, DGFiP, DREES, FMI, OpenFisca-France 177 ; registre complet avec empreintes : resultats/registre_telechargements.json",
        "modeles": sorted(modules),
        "parametres_sensibles": ["fermeture d'offre ρ (0,1-0,25)", "élasticité de l'emploi au coût du travail (calibrée, 0,2-0,6)",
                                 "effet du chômage sur les salaires (calibré)", "élasticité de l'investissement au coût du capital (fragile)",
                                 "prime de risque sur la dette (3 pb par point)", "délai de transmission des prix d'importation"],
        "incertitudes": "Intervalle à 90 % si demandé (tirages des paramètres estimés et calibrés) ; n'inclut ni l'incertitude sur les données, "
                        "ni celle sur la spécification des équations, ni celle sur l'environnement international.",
        "limites": ["Effets statiques des mesures socio-fiscales (pas de réaction de l'offre de travail ni du recours).",
                    "Modèle annuel, volumes non chaînés : horizon recommandé inférieur à 10 ans.",
                    "Pas de flux physiques d'énergie ni de matières.",
                    "Les taux d'intérêt n'agissent que sur l'investissement et la charge de la dette.",
                    "Aucune note globale n'est attribuée : les résultats sont des écarts conditionnels à un compte de référence."],
    }


def main():
    sc = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = executer(sc)
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else RACINE / "outputs" / (pathlib.Path(sys.argv[1]).stem + "_resultats.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    from simulateur import restitution
    restitution.ecrire_html(res, out.with_suffix(".html"))
    print(out, out.with_suffix(".html"), res["duree_s"], "s")


if __name__ == "__main__":
    main()
