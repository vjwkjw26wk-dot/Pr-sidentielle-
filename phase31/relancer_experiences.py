"""Relance de quelques expériences v0.8 (après une correction de code) et remplacement dans les fichiers de lots.
Usage : python3 phase31/relancer_experiences.py nom1 nom2 ..."""
import json, os, pathlib, sys, time
R = pathlib.Path(__file__).resolve().parents[1]
SORTIE = R / "phase31" / "resultats"
os.environ["SORTIE_SIMULATIONS"] = str(SORTIE)
sys.path[:0] = [str(R / "rapport"), str(R / "src"), str(R)]
import simulations as SIM  # noqa: E402
for nom in sys.argv[1:]:
    l, _, lib, cur = [e for e in SIM.EXPERIENCES if e[1] == nom][0]
    f = SORTIE / f"experiences_v08_{l}.json"
    res = json.loads(f.read_text())
    t0 = time.time()
    res[nom] = {"libelle": lib, **SIM.simuler(nom, cur)}
    f.write_text(json.dumps(res, ensure_ascii=False, default=float))
    print(l, nom, round(time.time() - t0), flush=True)
