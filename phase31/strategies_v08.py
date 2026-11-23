"""Phase 3.1 — recalcul des stratégies S1 à S5 de la v0.7 (définitions identiques) avec le modèle v0.8, et des
programmes de comparaison de la v0.6, dans trois configurations explicites :
- central : paramètres centraux ;
- réactions faibles et transmission lente : comportements « bas » (participation 0,1 ; épargne de précaution 0,1 ;
  pas de rigidité salariale asymétrique ; transfert de bénéfices 0,2 ; pas de canal de trésorerie ; pas de
  délocalisation ; incidence salariale de l'IS nulle ; cotisations entièrement transmises aux salaires à long terme ;
  R&D peu additionnelle) et fermeture lente (θ = 0,5 ; ρ = 0,1) ;
- réactions fortes et transmission rapide : comportements « hauts » et fermeture rapide (θ = 1,0 ; ρ = 0,3).
Pour chaque stratégie, la configuration la plus favorable et la plus défavorable sont identifiées a posteriori sur la
dette et le PIB (les deux ne coïncident pas toujours).
Sortie : phase31/resultats/strategies_v08_<programme>.json"""
import json, os, pathlib, sys, time
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport")]
from simulateur import executer as X  # noqa: E402
import simulations as SIM  # noqa: E402
OUT = R / "phase31" / "resultats"
CONFIGS = {"central": {}, "faible": {"comportements_v07": "basse", "fermeture_offre": 0.1},
           "fort": {"comportements_v07": "haute", "fermeture_offre": 0.3}}


def programmes():
    P = {}
    o = json.loads((R / "phase3" / "resultats" / "optimisation_v07.json").read_text())["strategies"]
    for k, s in o.items():
        cur = {}
        for lev, v in s["leviers"].items():
            val = {"ir_t1": 11, "ir_t4": 45, "taux_is": 25.8, "temps_travail": 35, "age_legal": 64}.get(lev, 0.0) + v
            cur[lev] = round(val) if lev == "age_legal" else round(val, 2)
        P[k] = cur
    S = json.loads((R / "rapport" / "resultats" / "strategie.json").read_text())["scenarios"]
    for k, v in S.items():
        if v.get("faisable"):
            P[f"v06_{k}"] = {a: float(b) for a, b in v["curseurs"].items()}
    f = R / "rapport" / "resultats" / "scenario_recommande.json"
    for k, v in json.loads(f.read_text()).items():
        P[f"v06_{k}"] = {a: float(b) for a, b in v["curseurs"].items()}
    return P


def resume(r):
    keep = ("trajectoires", "distribution", "inegalites", "groupes", "distribution_dynamique", "statique", "comportements")
    return {k: r.get(k) for k in keep}


if __name__ == "__main__":
    P = programmes()
    cfgs = sys.argv[1].split(",")
    for k in sys.argv[2:] or list(P):
        f = OUT / f"strategies_v08_{k}.json"
        out = json.loads(f.read_text()) if f.exists() else {"curseurs": P[k]}
        for c in cfgs:
            t0 = time.time()
            sc = {"nom": k, "horizon": 2047, "hypotheses": {"europe": True, "incertitude": 0, "profils": False, **CONFIGS[c]},
                  "mesures": [SIM.CUR[a]["mesure"](v) for a, v in P[k].items()]}
            out[c] = resume(X.executer(X.depuis_curseurs(sc)))
            f.write_text(json.dumps(out, ensure_ascii=False, default=float))
            print(k, c, round(time.time() - t0), flush=True)
