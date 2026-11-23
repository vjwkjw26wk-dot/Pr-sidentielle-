"""Phase 3.1 — causes des écarts entre v0.7 et v0.8, pour les stratégies et des mesures types.

Pour chaque programme, trois simulations v0.8 :
  A : v0.8 avec la fermeture de la v0.7 (θ = 1,5 ; ρ = 0,15 ; terme proportionnel 0,3 ; μ = 0,3) et l'incidence de la
      v0.7 (aucune incidence salariale de l'IS et des impôts de production ; cotisations entièrement transmises) ;
  B : v0.8 avec l'incidence de la v0.7 seulement ;
  C : v0.8 complète.
Décomposition de l'écart v0.8 − v0.7 :
  A − v0.7 : correction du défaut de code, recalage de la référence, offre de travail (18 cas types), distribution ;
  B − A    : fermeture estimée ;
  C − B    : incidence fiscale.
Sortie : phase31/resultats/decomposition_v07_v08.json"""
import json, pathlib, sys, time
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport"), str(R / "phase31")]
from simulateur import executer as X  # noqa: E402
import simulations as SIM  # noqa: E402
import strategies_v08 as SV  # noqa: E402
OUT = R / "phase31" / "resultats"
FERM_V07 = {"surcharges": {"THETA_ANTICIPATION": 1.5, "AMORTI_PRODUCTION": 0.3, "MU_IMPORT": 0.3}, "fermeture_offre": 0.15}
INC_V07 = {"niveaux_mesures": {"incidence": "basse"}}
EXP = {"cot_moins20": {"cotisations_employeurs": -20}, "is_baisse": {"taux_is": 20}, "is": {"taux_is": 30.5}, "production": {"impots_production": 10},
       "tva": {"tva": 1}, "csg": {"csg_activite": 1}, "rsa25": {"rsa": 25}, "ppa25": {"prime_activite": 25}, "invest20": {"investissement_public": 20},
       "age65": {"age_legal": 65}, "temps37": {"temps_travail": 37}, "recherche3": {"recherche": 3}}


def run(cur, hyp):
    sc = {"nom": "d", "horizon": 2047, "hypotheses": {"europe": True, "incertitude": 0, "profils": False, "distribution_dynamique": False, **hyp},
          "mesures": [SIM.CUR[a]["mesure"](v) for a, v in cur.items()]}
    tr = X.executer(X.depuis_curseurs(sc))["trajectoires"]
    return {k: {t: tr[k]["ecart"][t] for t in (2030, 2037, 2047)} for k in ("pib", "emploi", "chomage", "solde_pib", "dette_pib", "salaire", "pc")}


if __name__ == "__main__":
    P = SV.programmes()
    items = {**{k: P[k] for k in P if k.startswith("S")}, **EXP}
    f = OUT / "decomposition_v07_v08.json"
    res = json.loads(f.read_text()) if f.exists() else {}
    for k, cur in items.items():
        if k in res:
            continue
        t0 = time.time()
        res[k] = {"curseurs": cur, "A_fermeture_et_incidence_v07": run(cur, {**FERM_V07, **INC_V07}), "B_incidence_v07": run(cur, INC_V07)}
        f.write_text(json.dumps(res, default=float))
        print(k, round(time.time() - t0), flush=True)
