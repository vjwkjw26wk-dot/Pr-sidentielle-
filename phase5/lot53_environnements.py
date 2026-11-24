"""Phase 5, lot 5.3 : S1-S5 sous le régime principal dans les environnements calibrés p4 (σ = 0,45, prix frontière),
p4_sigma03, p4_sigma06 et p4_prix_v09 (équation de prix v0.9). Les programmes traduits sur p4/historique sont transférés
par écarts (ratios et différences) : approximation documentée, les exogènes de chaque environnement différant peu.
Usage : python3 phase5/lot53_environnements.py [conf ...]"""
import pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import pandas as pd
import m23_regimes as G, m25_programmes as P
OUT = pathlib.Path(__file__).parent / "resultats"
TR = pickle.load(open(OUT / "lot53_traductions.pkl", "rb"))
confs = sys.argv[1:] or ["p4", "p4_sigma03", "p4_sigma06", "p4_prix_v09"]
t0 = time.time(); rows = {}
for c in confs:
    env = G.Environnement.charger(c, "part_constante")
    ref = env.reference
    rows[(c, "référence", 2047)] = {"PIB (%)": float("nan"), "dette (pt PIB)": float(ref.dette_pib[2047]),
                                    "chômage (pt)": float(ref.chomage[2047])}
    for k, tr in TR.items():
        ec = G.evaluer(env, G.regime("R2"), P.programme(tr))["ecart"]
        for h in (5, 10, 20):
            rows[(c, k, 2026 + h)] = ec.loc[2026 + h].to_dict()
    print("fait", c, round(time.time() - t0), flush=True)
df = pd.DataFrame(rows).T; df.index.names = ["environnement", "stratégie", "année"]
df.to_csv(OUT / ("lot53_environnements_" + "_".join(confs) + ".csv"))
print(df.round(2).to_string())
