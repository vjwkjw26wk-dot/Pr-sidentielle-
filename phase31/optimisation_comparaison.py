"""Phase 3.1 — réoptimisation exploratoire : les solutions optimisées de la v0.7 sont-elles encore pertinentes ?

Pour chaque stratégie optimisée S1-S5 (phase 3), on évalue avec le métamodèle v0.8 (réponses des 68 expériences
relancées avec la v0.8) :
  - la composition optimale v0.7 (mêmes leviers, mêmes valeurs) ;
  - la composition réoptimisée v0.8, avec les critères distributifs statiques (comme en v0.7) puis après propagation
    macroéconomique (M16, option DISTRIB_DYN=1).
On vérifie les contraintes de chaque stratégie et on mesure la perte de la composition v0.7 sur l'objectif.
Les solutions robustes sont les leviers retenus dans les trois optimisations et fréquemment choisis quand les
préférences (poids des critères) varient.
Usage : DISTRIB_DYN=0|1 RES_OPTIM=… python3 phase31/optimisation_comparaison.py  → resultats/comparaison_optimisation_<s|d>.json
"""
import json
import os
import pathlib
import sys

import numpy as np

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "phase3")]
import optimisation as O  # noqa: E402

DYN = O.DISTRIB_DYN
V07 = json.loads((R / "phase3" / "resultats" / "optimisation_v07.json").read_text())
V08 = json.loads((O.RES / "optimisation_v07.json").read_text())


def x_de(var, lev):
    x = np.zeros(len(var))
    for lv, val in lev.items():
        s = 1 if val > 0 else -1
        idx = [i for i, v in enumerate(var) if v[0] == lv and v[1] == s]
        if not idx:      # levier symétrique déclaré dans un seul sens
            idx = [i for i, v in enumerate(var) if v[0] == lv]
            x[idx[0]] = val * var[idx[0]][1]
        else:
            x[idx[0]] = abs(val)
    return x


def contraintes_ok(res, cons):
    out = []
    for c, t, op, b in cons:
        if c == "decile_min":
            v = min(res["deciles"])
        else:
            v = res[t][c]
        ok = v <= b + 1e-6 if op == "<=" else v >= b - 1e-6
        out.append({"critere": c, "horizon": t, "op": op, "borne": b, "valeur": v, "respectee": bool(ok)})
    return out


def objectif(res, obj, t=2037):
    if obj == "tchebychev":
        nz = V08["normalisation"]
        return min(O.CRITERES[c][1] * res[t][c] / nz[c] for c in O.CRITERES if c in nz and nz[c] > 0)
    return sum(w * res[t][c] for c, w in obj.items())


def main():
    exp = O.charger()
    var = O.metamodele(exp, ("A", "B"))
    out = {}
    for k, s7 in V07["strategies"].items():
        s8 = V08["strategies"][k]
        r7 = O.evaluer(var, x_de(var, s7["leviers"]))
        r8 = O.evaluer(var, x_de(var, s8["leviers"]))
        t_obj = 2042 if k == "S3_productivite" else 2037
        o7, o8 = objectif(r7, s8["objectif"], t_obj), objectif(r8, s8["objectif"], t_obj)
        communs = sorted(set(s7["leviers"]) & set(s8["leviers"]))
        out[k] = {"leviers_v07": s7["leviers"], "leviers_v08": s8["leviers"], "communs": communs,
                  "objectif_v07_eval_v08": o7, "objectif_v08": o8, "perte_relative": (o8 - o7) / abs(o8) if o8 else None,
                  "contraintes_v07_eval_v08": contraintes_ok(r7, s8["contraintes"]), "contraintes_v08": contraintes_ok(r8, s8["contraintes"]),
                  "v07_eval_v08": {str(t): r7[t] for t in O.HORIZONS}, "v08": {str(t): r8[t] for t in O.HORIZONS},
                  "deciles_v07_eval_v08": r7["deciles"], "deciles_v08": r8["deciles"]}
        nb = sum(not c["respectee"] for c in out[k]["contraintes_v07_eval_v08"])
        print(k, "objectif v07→v08 %.2f / optimum v08 %.2f ; contraintes violées : %d ; leviers communs : %s" % (o7, o8, nb, communs))
    f7 = V07["perimetres"]["principal"]["robustesse_preferences"]["frequence"]
    f8 = V08["perimetres"]["principal"]["robustesse_preferences"]["frequence"]
    out["frequences"] = {k: {"v07": f7.get(k, 0.0), "v08": f8.get(k, 0.0)} for k in sorted(set(f7) | set(f8), key=lambda k: -f8.get(k, 0.0))}
    out["pareto"] = {"v07": {k: v for k, v in V07["perimetres"]["principal"]["pareto"].items() if not isinstance(v, list)},
                     "v08": {k: v for k, v in V08["perimetres"]["principal"]["pareto"].items() if not isinstance(v, list)}}
    (R / "phase31" / "resultats" / f"comparaison_optimisation_{'d' if DYN else 's'}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
