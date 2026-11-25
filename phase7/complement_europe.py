"""Correction (25 novembre 2026) des variantes européennes de la campagne : le choc de prime souveraine de la variante
« tension » est une réponse au programme et ne doit pas figurer dans la simulation de référence. Recalcule
europe:conforme / contentieux / tension pour un candidat et met à jour <candidat>.pkl et <candidat>_synthese.csv.
Usage : python3 phase7/complement_europe.py <candidat>"""
import copy, pathlib, pickle, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R), str(R / "phase7")]
import pandas as pd
import m23_regimes as G, m25_programmes as P, m26_europe_institutions as U, m27_corpus as C
OUT = R / "phase7" / "resultats"; HORIZONS = {5: 2031, 10: 2036, 20: 2046}
cand = sys.argv[1]
sys.argv = [sys.argv[0], cand, "--rapide"]
src = (R / "phase7" / "campagne.py").read_text()
ns = {"__file__": str(R / "phase7" / "campagne.py")}
exec(src[:src.index("env_h = G.Environnement")].replace("cand = sys.argv[1]", f"cand = {cand!r}"), ns)
indicateurs = ns["indicateurs"]
env_h = G.Environnement.charger("p4", "historique"); env = G.Environnement.charger("p4", "part_constante")
d = pickle.load(open(OUT / f"{cand}.pkl", "rb"))
liste, _ = C.mesures(cand, env.reference, "conforme")
pA = None
for scen in ("conforme", "contentieux", "tension"):
    sc = U.SCENARIOS[scen]
    ls, _ = C.mesures(cand, env.reference, scen)
    if ls == liste and pA is not None:
        ps = pA
    else:
        ps = P.programme(P.traduire([x[:3] for x in ls], env_h, f"{cand}_{scen}", microsimulation="calcul"))
        if ls == liste:
            pA = ps
    reg = G.regime("R2", monetaire=U.regime_monetaire(sc))
    sc0 = copy.deepcopy(sc); sc0.choc_ecart_pb = {}
    ref0 = G.simuler(env, G.regime("R2", monetaire=U.regime_monetaire(sc0)))
    d["resultats"][f"europe:{scen}"] = indicateurs(G.evaluer(env, reg, U.programme(sc, ps), ref=ref0))
    print(cand, scen, flush=True)
pickle.dump(d, open(OUT / f"{cand}.pkl", "wb"))
res = d["resultats"]
syn = pd.concat({k: v.loc[list(HORIZONS.values())].rename(index={y: h for h, y in HORIZONS.items()}) for k, v in res.items()},
                names=["simulation", "horizon"])
syn.to_csv(OUT / f"{cand}_synthese.csv")
print("terminé")
