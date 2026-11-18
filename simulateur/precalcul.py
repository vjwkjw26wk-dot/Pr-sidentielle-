"""Précalcul des variantes élémentaires pour l'interface de test (version 0.3).

Chaque curseur du catalogue (`catalogue.CURSEURS`) est simulé seul, aux points de sa grille, par la chaîne complète
(compte de référence recalé M8, M4/M10 pour les mesures des ménages, M9 pour les retraites, M11 pour la zone euro,
M13 pour les réactions des hauts revenus), avec entrée en vigueur en 2028. L'interface combine ensuite les curseurs
par addition des écarts, avec interpolation linéaire entre les points (et 0 à la valeur actuelle) : approximation
qui ignore les interactions entre mesures, à vérifier par une exécution complète (`simulateur.executer`).
Sortie : outputs/variantes_elementaires.json (écrit au fur et à mesure ; les variantes déjà présentes et calculées
sur le même compte de référence sont conservées).
Usage : python3 -m simulateur.precalcul [clé de curseur ...]
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import traceback

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import executer as X, catalogue as CAT  # noqa: E402

INDICATEURS = ["pib", "croissance", "emploi", "chomage", "inflation", "pc", "rdb", "salaire", "c", "fbcf", "x", "m",
               "solde_pib", "dette_pib", "recettes_pib", "depenses_pib", "interets_pib", "taux_apparent", "pensions_pib",
               "retraites_pour_100_actifs", "part_industrie", "emploi_industrie", "population_active", "rnb", "taux_epargne",
               "solde_exterieur_pib"]
HORIZON = 2032
VERSION = "0.6"


def main():
    sortie = RACINE / "outputs" / "variantes_elementaires.json"
    res = json.loads(sortie.read_text()) if sortie.exists() else {}
    if res.get("version") != VERSION:
        res = {"version": VERSION, "variantes": {}}
    t0 = time.time()
    seule = sys.argv[1:]
    hyp = {"europe": True, "incertitude": 0, "profils": True}
    if "reference" not in res:
        r = X.executer({"nom": "reference", "horizon": HORIZON, "hypotheses": hyp, "mesures": []})
        tr = r["trajectoires"]
        res["reference"] = {i: tr[i]["reference"] for i in INDICATEURS}
        res["unites"] = {i: tr[i]["unite_ecart"] for i in INDICATEURS}
        res["libelles"] = {i: X.VARIABLES[i] for i in INDICATEURS}
        res["transparence"] = r["transparence"]
        sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
    import m8_reference as RF
    res.setdefault("references", {})
    for nom, lib in RF.VARIANTES_REFERENCE.items():
        if nom in res["references"] or (seule and "references" not in seule):
            continue
        r = X.executer({"nom": nom, "horizon": HORIZON, "hypotheses": {**hyp, "reference": nom, "profils": False}, "mesures": []})
        res["references"][nom] = {"libelle": lib, "niveaux": {i: r["trajectoires"][i]["reference"] for i in INDICATEURS}}
        sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
        print(f"référence {nom}", flush=True)
    for c in CAT.CURSEURS:
        cle = c["cle"]
        if seule and cle not in seule:
            continue
        for val in c["points"]:
            k = f"{val:g}"
            if k in res["variantes"].get(cle, {}) and not seule:
                continue
            sc = {"nom": f"{cle} {k}", "horizon": HORIZON, "hypotheses": hyp, "mesures": [c["mesure"](val)]}
            try:
                r = X.executer(sc)
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                continue
            tr = r["trajectoires"]
            e = {i: tr[i]["ecart"] for i in INDICATEURS}
            e["emploi_milliers"] = {a: tr["emploi"]["scenario"][a] - tr["emploi"]["reference"][a] for a in tr["emploi"]["ecart"]}
            e["emploi_industrie_milliers"] = {a: tr["emploi_industrie"]["scenario"][a] - tr["emploi_industrie"]["reference"][a]
                                              for a in tr["emploi_industrie"]["ecart"]}
            res["variantes"].setdefault(cle, {})[k] = {"ecarts": e, "statique": r["statique"], "distribution": r["distribution"],
                                                     "profils": r["profils"], "europe": r["europe"],
                                                     "comportements": r.get("comportements")}
            sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
            print(f"{cle} {k} : {r['duree_s']} s (total {time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
