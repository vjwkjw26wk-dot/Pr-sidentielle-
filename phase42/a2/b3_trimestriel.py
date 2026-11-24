"""A.2 — Système prix-salaires trimestriel (M20) : estimations 1997-2019, stabilité, simulation conjointe 2021-2024,
réponses de long terme."""
import pathlib, sys
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import m20_trimestriel as T
d = T.donnees()
s, rs = T.part_domestique(d)
print(f"Part domestique dans le prix à la consommation (niveau, 1997-2019) : s = {s:.2f} (e.t. {rs.bse.iloc[1]:.2f})")
R = {}
for eq in ("W", "W+anticipations", "P", "P+tension", "P+anticipations", "C"):
    for nom, (a, b) in {"1997-2019": ("1997Q1", "2019Q4"), "1997-2007": ("1997Q1", "2007Q4"), "2010-2019": ("2010Q1", "2019Q4")}.items():
        R[(eq, nom)] = T.estimer(d, eq, a, b, s=s)
def tab(eq):
    cols = {}
    for nom in ("1997-2019", "1997-2007", "2010-2019"):
        r = R[(eq, nom)]
        cols[nom] = {k: f"{r.params[k]:.3f} ({r.bse[k]:.3f})" for k in r.params.index}
        if eq.startswith("W"):
            cols[nom]["indexation cumulée (5 trim.)"] = f"{sum(r.params[k] for k in r.params.index if k.startswith('dlpc')):.2f}"
        if eq.startswith("P"):
            cols[nom]["transmission cumulée du CSU (3 trim.)"] = f"{sum(r.params[k] for k in r.params.index if k.startswith('dlcsu')):.2f}"
        cols[nom]["n"] = int(r.nobs); cols[nom]["R2"] = round(r.rsquared, 2)
    return pd.DataFrame(cols)
pd.set_option("display.width", 220)
for eq in ("W", "W+anticipations", "P", "P+tension", "P+anticipations", "C"):
    print(f"\n=== {eq}\n" + tab(eq).to_string())
# simulation conjointe hors échantillon 2021-2024
print("\n=== Simulation conjointe 2021T1-2024T4 (coefficients 1997-2019), croissance annuelle moyenne (%) simulée / observée")
for eqw, eqp in (("W", "P"), ("W+anticipations", "P"), ("W", "P+anticipations"), ("W+anticipations", "P+anticipations")):
    sim = T.simuler_systeme(d, R[(eqw, "1997-2019")], R[(eqp, "1997-2019")], R[("C", "1997-2019")], s, "2021Q1", "2024Q4", eqw, eqp)
    ann = lambda x: x.groupby(x.index.year).mean()
    out = {}
    for k in ("lw", "lpva", "lpc"):
        ss, oo = ann(np.exp(sim[k])), ann(np.exp(d[k]))
        out[k] = " ".join(f"{100 * np.log(ss[y] / (oo[y - 1] if y == 2021 else ss[y - 1])):.1f}/{100 * np.log(oo[y] / oo[y - 1]):.1f}" for y in (2022, 2023, 2024))
        out[k + " niveau 2024T4 (%)"] = round(100 * float(sim[k].iloc[-1] - d[k]["2024Q4"]), 1)
    print(f"{eqw} + {eqp} : " + " | ".join(f"{k} {v}" for k, v in out.items()))
# réponses de long terme du système estimé
print("\n=== Réponses du système homogène (coefficients 1997-2019), écart en % : trimestres 1, 4, 12, 20, 40, 60")
for choc in ("salaire", "import"):
    for eqw, eqp in (("W", "P"), ("W+anticipations", "P")):
        rr = T.reponse_choc(R[(eqw, "1997-2019")], R[(eqp, "1997-2019")], R[("C", "1997-2019")], s, choc, 60, eqw, eqp)
        print(f"{choc:8s} {eqw:16s}: " + " | ".join(f"{k} " + " ".join(f"{rr[k].iloc[i]:.2f}" for i in (0, 3, 11, 19, 39, 59)) for k in rr))
