"""Recalcule les variantes « OAT 3,82 % » (A:oat_382, B:oat_382) d'une campagne après correction du transfert des
variantes d'environnement au régime monétaire (2026-11-24). Usage : python3 phase7/complement_oat.py <candidat>"""
import json, pathlib, pickle, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R), str(R / "phase7")]
import pandas as pd
import m23_regimes as G, m25_programmes as P, m27_corpus as C
cand = sys.argv[1]
OUT = R / "phase7" / "resultats"
d = pickle.load(open(OUT / f"{cand}.pkl", "rb"))
import importlib.util
spec = importlib.util.spec_from_file_location("camp_ind", R / "phase7" / "campagne.py")
src = (R / "phase7" / "campagne.py").read_text()
ns = {}
exec(src[src.index("def indicateurs"):src.index("def evaluer")], {"np": __import__("numpy"), "pd": pd}, ns)
indicateurs = ns["indicateurs"]
env_h = G.Environnement.charger("p4", "historique")
env = G.Environnement.charger("p4", "part_constante")
liste = [tuple(x) for x in d["meta"]["mesures"]]
pA = P.programme(P.traduire([x[:3] for x in liste], env_h, f"{cand}_A", microsimulation="calcul"))
ob = d["meta"]["objectif"]
obj = G.ObjectifBudgetaire(cibles={int(k): v for k, v in ob["cibles"].items()}, parts=ob["parts"], debut=2028)
voat = G.variante_oat()
REG = G.regime("R2")
d["resultats"]["A:oat_382"] = indicateurs(G.evaluer(env, REG, pA, variante_env=voat))
eB = G.evaluer(env, REG, pA, objectif=obj, variante_env=voat)
d["resultats"]["B:oat_382"] = indicateurs(eB)
d["meta"]["B_oat_ecart_cible"] = eB["variante"]["ecart_cible"]
pickle.dump(d, open(OUT / f"{cand}.pkl", "wb"))
H = {5: 2031, 10: 2036, 20: 2046}
syn = pd.concat({k: v.loc[list(H.values())].rename(index={y: h for h, y in H.items()}) for k, v in d["resultats"].items()},
                names=["simulation", "horizon"])
syn.to_csv(OUT / f"{cand}_synthese.csv")
print(cand, "OAT recalculé")
