"""Précalcul des variantes élémentaires pour l'interface de test.

Chaque mesure du catalogue est simulée seule, sur une grille d'intensités, par la chaîne complète (M1, M4/M10 pour les
mesures socio-fiscales, M9 pour l'âge légal, M8, M11). L'interface combine ensuite les mesures choisies par addition
des écarts, avec interpolation linéaire entre les points de la grille : c'est une approximation (les interactions
entre mesures sont ignorées), à vérifier par une exécution complète du scénario (`simulateur.executer`).
Sortie : outputs/variantes_elementaires.json (écrit au fur et à mesure).
Usage : python3 -m simulateur.precalcul
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import traceback

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import executer as X  # noqa: E402

INDICATEURS = ["pib", "emploi", "chomage", "pc", "rdb", "solde_pib", "dette_pib", "c", "fbcf", "x", "m", "salaire"]

# grille : (identifiant de curseur, valeur affichée, mesure du catalogue)
GRILLE = {
    "depense_publique": [(v, {"type": "depense_publique", "parametres": {"points_pib": v, "debut": 2024}}) for v in (-2.0, -1.0, 1.0, 2.0)],
    "transferts_menages": [(v, {"type": "transferts_menages", "parametres": {"points_pib": v, "debut": 2024}}) for v in (-1.0, 1.0)],
    "taux_is": [(v, {"type": "taux_is", "parametres": {"taux": v, "debut": 2024}}) for v in (15.0, 20.0, 30.0, 33.3)],
    "ir_premiere_tranche": [(v, {"type": "bareme_ir", "parametres": {"taux": {1: v / 100}}}) for v in (9.0, 13.0, 15.0)],
    "ir_seuils": [(v, {"type": "bareme_ir", "parametres": {"seuils_facteur": 1 + v / 100, "decote_facteur": 1 + v / 100,
                                                           "plafond_qf_facteur": 1 + v / 100}}) for v in (-3.0, 3.0)],
    "rsa": [(v, {"type": "rsa", "parametres": {"facteur": 1 + v / 100}}) for v in (-10.0, 10.0, 25.0)],
    "prime_activite": [(v, {"type": "prime_activite", "parametres": {"facteur": 1 + v / 100}}) for v in (-10.0, 10.0, 25.0)],
    "allocations_familiales": [(v, {"type": "allocations_familiales", "parametres": {"facteur": 1 + v / 100}}) for v in (-10.0, 10.0, 25.0)],
    "age_legal": [(v, {"type": "age_legal", "parametres": {"regle": r}}) for v, r in ((62.0, "2010"), (65.0, "65"), (66.0, "66"))],
    "salaires": [(v, {"type": "salaires", "parametres": {"hausse": v / 100, "debut": 2024}}) for v in (-2.0, 2.0, 5.0)],
    "reindustrialisation": [(v, {"type": "reindustrialisation", "parametres": {"baisse_parts_importees": v / 100, "duree": 5, "surcout": 0.10, "debut": 2024}})
                            for v in (5.0, 10.0, 20.0)],
    "energie_import": [(v, {"type": "energie_import", "parametres": {"hausse": v / 100, "debut": 2024}}) for v in (-20.0, 20.0, 50.0)],
}


def main():
    sortie = RACINE / "outputs" / "variantes_elementaires.json"
    res = json.loads(sortie.read_text()) if sortie.exists() else {"variantes": {}}
    t0 = time.time()
    seule = sys.argv[1:]  # éventuellement une liste de curseurs à (re)calculer
    for cle, points in GRILLE.items():
        if seule and cle not in seule:
            continue
        for val, mesure in points:
            k = f"{val:g}"
            if k in res["variantes"].get(cle, {}) and not seule:
                continue
            sc = {"nom": f"{cle} {k}", "base": 2022, "horizon": 2030, "hypotheses": {"europe": True, "incertitude": 0, "profils": True},
                  "mesures": [mesure]}
            try:
                r = X.executer(sc)
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                continue
            tr = r["trajectoires"]
            e = {i: {a: tr[i]["ecart"][a] for a in tr[i]["ecart"]} for i in INDICATEURS}
            e["emploi_milliers"] = {a: tr["emploi"]["scenario"][a] - tr["emploi"]["reference"][a] for a in tr["emploi"]["ecart"]}
            res["variantes"].setdefault(cle, {})[k] = {"ecarts": e, "statique": r["statique"], "distribution": r["distribution"],
                                                     "profils": r["profils"], "europe": r["europe"]}
            if "reference" not in res:
                res["reference"] = {i: tr[i]["reference"] for i in INDICATEURS}
            sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
            print(f"{cle} {k} : {r['duree_s']} s (total {time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
