"""Phase 4.2, chantier A : équation de salaires en trimestriel (secteur marchand = ensemble − O-Q), pour identifier
l'indexation de court terme sur les prix. Sources : Eurostat namq_10_a10 (D1, B1G, CP et CLV15, CVS-CJO),
namq_10_a10_e (salariés, milliers, CVS-CJO), namq_10_fcs (P31_S14), Insee BDM 001688526 (chômage BIT, trimestriel).
Δln w = c + Σ_{i=0..4} b_i Δln pc_{t−i} + d Δln prod + λ (ln w − ln pva − ln prod)_{t−1} + γ (u − u*)_{t−1}
Estimation 1997T1-2019T4 ; simulation dynamique 2021T1-2024T4 (prix, VA, productivité, chômage observés)."""
import json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd, statsmodels.api as sm
from telechargement import jsonstat_dict
import m7_series as S
L = lambda f: pd.Series(jsonstat_dict(json.loads((R / "data" / "raw" / f).read_text())))
a, e, c = L("eurostat_namq_10_a10_FR.json"), L("eurostat_namq_10_a10_e_FR.json"), L("eurostat_namq_10_fcs_FR.json")
a1 = L("eurostat_namq_10_a10_D1_FR.json")
def q(s, *k):
    return pd.Series({kk[-1]: v for kk, v in s.items() if tuple(kk[:-1]) == k}, dtype=float).sort_index()
D1 = q(a1, "SA", "TOTAL") - q(a1, "SA", "O-Q")
VA = q(a, "CP_MEUR", "TOTAL", "B1G") - q(a, "CP_MEUR", "O-Q", "B1G")
VAv = q(a, "CLV15_MEUR", "TOTAL", "B1G") - q(a, "CLV15_MEUR", "O-Q", "B1G")       # approximation (volumes chaînés)
SAL = q(e, "TOTAL", "SA") - q(e, "O-Q", "SA")
PC = q(c, "CP_MEUR") / q(c, "CLV15_MEUR")
U = S.bdm("001688526").astype(float)
idx = sorted(set(D1.index) & set(SAL.index) & set(PC.index) & set(VAv.index))
d = pd.DataFrame({"lw": np.log(D1 / SAL), "lpva": np.log(VA / VAv), "lprod": np.log(VAv / SAL), "lpc": np.log(PC), "u": U}).loc[idx]
d.index = pd.PeriodIndex(d.index, freq="Q")
from statsmodels.tsa.filters.hp_filter import hpfilter
cyc, tr = hpfilter(d.u.dropna(), lamb=1600)
d["ugap"] = cyc
for k in ("lw", "lpc", "lprod"):
    d["d" + k] = d[k].diff()
for i in range(1, 5):
    d[f"dlpc_{i}"] = d.dlpc.shift(i)
d["ecm"] = (d.lw - d.lpva - d.lprod).shift(1)
d["ugap_1"] = d.ugap.shift(1)
X0 = ["dlpc"] + [f"dlpc_{i}" for i in range(1, 5)] + ["dlprod", "ecm", "ugap_1"]
res = {}
for nom, fin in (("1997-2019", "2019Q4"), ("1997-2024 (avec l'épisode inflationniste)", "2024Q4")):
    dd = d.loc["1997Q1":fin].dropna(subset=X0 + ["dlw"])
    r = sm.OLS(dd.dlw, sm.add_constant(dd[X0])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    bsum = sum(r.params[k] for k in X0 if k.startswith("dlpc"))
    V = r.cov_params().loc[[k for k in X0 if k.startswith("dlpc")], [k for k in X0 if k.startswith("dlpc")]]
    res[nom] = r
    print(f"\n=== {nom} (n = {int(r.nobs)})")
    print(pd.DataFrame({"coef": r.params, "e.t.": r.bse}).round(3).T.to_string())
    print(f"indexation cumulée sur 5 trimestres : {bsum:.2f} (e.t. {np.sqrt(V.values.sum()):.2f}) ; "
          f"indexation de court terme (trimestre) : {r.params['dlpc']:.2f} ; retour de la part salariale par an ≈ {4 * r.params['ecm']:.2f}")
# simulation dynamique 2021T1-2024T4 avec les coefficients pré-2020
r = res["1997-2019"]
lw = {pd.Period("2020Q4", "Q"): float(d.lw["2020Q4"])}
per = pd.period_range("2021Q1", "2024Q4", freq="Q")
for t in per:
    x = {k: float(d.loc[t, k]) for k in X0 if k != "ecm"}
    x["ecm"] = lw[t - 1] - float(d.lpva[t - 1]) - float(d.lprod[t - 1])
    lw[t] = lw[t - 1] + r.params["const"] + sum(r.params[k] * x[k] for k in X0)
sim = pd.Series(lw)
ann = lambda s: s.groupby(s.index.year).mean()
gw_s = 100 * ann(np.exp(sim)).pipe(np.log).diff(); gw_o = 100 * ann(np.exp(d.lw)).pipe(np.log).diff()
print("\nCroissance annuelle du salaire par tête marchand (%) — simulé avec coefficients 1997-2019 / observé :")
print(pd.DataFrame({"simulé": gw_s.loc[2022:2024], "observé": gw_o.loc[2022:2024]}).round(2).T.to_string())
print(f"erreur de niveau fin 2024 : {100 * (sim[per[-1]] - d.lw[per[-1]]):.2f} %")

# --- équivalent annuel : réponse du salaire (moyenne annuelle) à une hausse permanente de 1 % du niveau des prix
#     répartie uniformément sur l'année 1 (0,25 % par trimestre), prix de VA suivant les prix à la consommation
#     (cas d'un choc domestique) ou restant fixes (cas d'un choc de prix importés) ; productivité inchangée.
for cas, pva_suit in (("prix de VA suivant les prix (choc domestique)", True), ("prix de VA fixes (choc importé)", False)):
    lw, lpc, lpva = [0.0] * 8, [0.0] * 8, [0.0] * 8
    for t in range(8, 8 + 40):
        dpc = 0.0025 if 8 <= t < 12 else 0.0
        lpc.append(lpc[-1] + dpc)
        lpva.append(lpc[-1] if pva_suit else 0.0)
        dl = sum(r.params[k] * ((lpc[t - i] - lpc[t - i - 1])) for i, k in enumerate(["dlpc", "dlpc_1", "dlpc_2", "dlpc_3", "dlpc_4"]))
        dl += r.params["ecm"] * (lw[-1] - lpva[t - 1])
        lw.append(lw[-1] + dl)
    an = [np.mean(lw[8 + 4 * k: 12 + 4 * k]) / 0.01 for k in range(6)]
    pn = [np.mean(lpc[8 + 4 * k: 12 + 4 * k]) / 0.01 for k in range(6)]
    print(f"{cas} : salaire / prix (moyennes annuelles), années 1 à 6 : " + ", ".join(f"{a:.2f}/{p:.2f}" for a, p in zip(an, pn)))
