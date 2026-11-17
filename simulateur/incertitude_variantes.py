"""Marges d'incertitude des écarts, estimées par Monte-Carlo (M12) sur des mesures représentatives (version 0.4).

Pour chaque mesure, 20 tirages des paramètres estimés (matrice de covariance) et calibrés (plages) ; on retient, par
indicateur et par année, la demi-largeur de l'intervalle à 90 % rapportée à la valeur absolue de l'écart central.
L'interface applique la médiane de ces rapports à tous les curseurs : c'est une approximation (les mesures n'ont pas
toutes la même incertitude relative), documentée comme telle.
Sortie : outputs/incertitude_variantes.json.  Usage : python3 -m simulateur.incertitude_variantes
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import executer as X, catalogue as CAT  # noqa: E402

REPRESENTATIVES = [("sante", 10), ("ir_t1", 9), ("age_legal", 62), ("tva", 2), ("cotisations_employeurs", -15), ("smic", 5), ("droits_douane", 10)]
CORRESP = {"pib": "pib", "emploi": "emploi", "prix": "pc", "solde": "solde_pib", "dette": "dette_pib"}


def main(n=20):
    cur = {c["cle"]: c for c in CAT.CURSEURS}
    sortie = RACINE / "outputs" / "incertitude_variantes.json"
    res = json.loads(sortie.read_text()) if sortie.exists() else {"mesures": {}}
    for cle, v in REPRESENTATIVES:
        if cle in res["mesures"]:
            continue
        r = X.executer({"nom": cle, "horizon": 2032, "hypotheses": {"europe": False, "incertitude": n, "profils": False},
                        "mesures": [cur[cle]["mesure"](v)]})
        rap = {}
        for k, ind in CORRESP.items():
            for a, d in (r["incertitude"] or {}).items():
                tr = r["trajectoires"][ind]
                e = (tr["scenario"][int(a)] - tr["reference"][int(a)]) if ind == "emploi" else tr["ecart"][int(a)]   # emploi : milliers
                if abs(e) > 1e-3:
                    lo, hi = d[k]
                    rap.setdefault(ind, {})[int(a)] = (hi - lo) / 2 / abs(e)
        res["mesures"][cle] = {"valeur": v, "rapports": rap, "intervalles": r["incertitude"]}
        sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
        print(cle, {k: {a: round(x, 2) for a, x in d.items()} for k, d in rap.items()}, flush=True)
    med = {}
    for ind in CORRESP.values():
        for a in (2028, 2030, 2032):
            L = [m["rapports"].get(ind, {}).get(a) or m["rapports"].get(ind, {}).get(str(a)) for m in res["mesures"].values()]
            L = [x for x in L if x is not None]
            if L:
                med.setdefault(ind, {})[a] = min(1.5, statistics.median(L))
    res["mediane"] = med
    sortie.write_text(json.dumps(res, ensure_ascii=False, default=float), encoding="utf-8")
    print("médiane", med)


if __name__ == "__main__":
    main()
