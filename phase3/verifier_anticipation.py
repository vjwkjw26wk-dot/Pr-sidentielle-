"""Sensibilité des stratégies à l'intensité de l'anticipation dans la fermeture (θ = 1,0 et 2,0 au lieu de 1,5).
Sortie : phase3/resultats/anticipation_v07.json"""
import json, os, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]
os.environ["SORTIE_SIMULATIONS"] = str(R / "phase3" / "resultats")
sys.path[:0] = [str(R / "phase3"), str(R / "rapport"), str(R / "src"), str(R)]
import verifier_strategies as VS  # noqa: E402
from simulations import simuler  # noqa: E402
P = VS.programmes()
f = R / "phase3" / "resultats" / "anticipation_v07.json"
out = json.loads(f.read_text()) if f.exists() else {}
for k in sys.argv[1:] or [p for p in P if p.startswith("S")]:
    for niv in ("anticipation_faible", "anticipation_forte"):
        r = simuler(k, P[k], hyp={"comportements_v07": niv})
        out[f"{k}|{niv}"] = {"curseurs": P[k], "traj": r["traj"]}
        f.write_text(json.dumps(out, ensure_ascii=False, default=float))
        print(k, niv, "ok", flush=True)
