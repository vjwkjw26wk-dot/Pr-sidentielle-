"""A.2 — Prix de VA (panel de 25 branches, annuel) : coût du capital dans la cible de prix, et transmission propre
des subventions sur salaires (CICE) ; hétérogénéité de la transmission (tension, exposition, niveau de marge).

Coût d'usage du capital par unité de VA (Jorgenson) : cku = p_I (r + δ − π_I^e) K / q, avec r = taux de l'OAT 10 ans
(Insee/Eurostat, série taux_long de M7), δ = taux de déclassement implicite de la branche (I − ΔK)/K_{−1} (moyenne
1997-2019), π_I^e = inflation moyenne du prix de l'investissement sur 5 ans (anticipation adaptative).
Cible de long terme : ln pva = μ + θ ln csu + (1 − θ) ln cku  (frontière des prix de facteurs, approximation log-linéaire ;
θ ≈ part du travail si les prix suivent les coûts complets) ; test de l'homogénéité et estimation libre de θ."""
import pathlib, sys
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parents[2] / "src")]
import numpy as np, pandas as pd, statsmodels.api as sm
import m7_series as S, m7_equations as E, m8_modele as M
p = S.panel_branches(); m = S.macro()
sv = M.taux_subvention_salaires()
p = p.sort_values(["branche", "annee"]).copy()
p["s_sub"] = p.annee.map(sv).fillna(0.0)
p["clu_brut"] = p.wb / p.hs * p.h / p.q
p["clu_net"] = p.clu_brut * (1 - p.s_sub)
r = (m.taux_long / 100).reindex(p.annee).values
p["r"] = r
out = []
for b, d in p.groupby("branche"):
    d = d.copy()
    delta = ((d.i - d.k.diff()) / d.k.shift(1)).loc[(d.annee >= 1997) & (d.annee <= 2019)].mean()
    d["pi_e"] = np.log(d.pi).diff().rolling(5, min_periods=3).mean().shift(1)
    d["uc"] = d.pi * np.maximum(d.r + delta - d.pi_e, 0.02)          # plancher de 2 % : coût d'usage strictement positif
    d["lcku"] = np.log(d.uc * d.k.shift(1) / d.q)
    d["lpva"] = np.log(d.va_cp / d.q)
    d["lclu_b"] = np.log(d.clu_brut); d["lclu_n"] = np.log(d.clu_net)
    d["dlpva"] = d.lpva.diff(); d["dlclu_b"] = d.lclu_b.diff(); d["dlsub"] = np.log(1 - d.s_sub).diff()
    d["dlclu_n"] = d.lclu_n.diff(); d["dlq"] = np.log(d.q).diff(); d["dlcku"] = d.lcku.diff()
    for k in ("lpva", "lclu_n", "lcku"):
        d[k + "_1"] = d[k].shift(1)
    d["marge_1"] = (1 - d.clu_net * d.q / d.va_cp).shift(1)         # taux de marge (1 − part du coût du travail)
    d["delta"] = delta
    out.append(d)
p = pd.concat(out)
p["tucd"] = E.tension_capacites(p.reset_index(drop=True)).values / 100
p["expose"] = p.branche.isin(S.INDUSTRIE).astype(float)
def est(cols, debut=1998, fin=2019, data=p):
    d = data[(data.annee >= debut) & (data.annee <= fin)]
    X = pd.concat([d[cols], pd.get_dummies(d.branche, prefix="fe", drop_first=True, dtype=float)], axis=1)
    ok = X.notna().all(axis=1) & d.dlpva.notna() & np.isfinite(X).all(axis=1)
    w = d.groupby("annee").va_cp.transform(lambda s: s / s.sum())
    return sm.WLS(d.dlpva[ok], sm.add_constant(X[ok]), weights=w[ok]).fit(cov_type="cluster", cov_kwds={"groups": d.annee[ok]})
def show(nom, r, keys):
    print(f"\n--- {nom} (n = {int(r.nobs)}, R2 = {r.rsquared:.2f})")
    print("   " + " ; ".join(f"{k} {r.params[k]:.3f} ({r.bse[k]:.3f})" for k in keys))
# 1. référence v0.9 (coût net)
p["ecm_v09"] = p.lpva_1 - p.lclu_n_1
r0 = est(["dlclu_n", "dlq", "tucd", "ecm_v09"]); show("V0 : cible = CSU (v0.9)", r0, ["dlclu_n", "dlq", "ecm_v09"])
# 2. cible libre : λ ln pva_{−1} + φ1 ln csu_{−1} + φ2 ln cku_{−1}
r1 = est(["dlclu_n", "dlq", "tucd", "lpva_1", "lclu_n_1", "lcku_1"])
lam, f1, f2 = r1.params["lpva_1"], r1.params["lclu_n_1"], r1.params["lcku_1"]
show("K1 : cible libre (CSU et coût du capital)", r1, ["dlclu_n", "lpva_1", "lclu_n_1", "lcku_1"])
print(f"   θ (poids du CSU à long terme) = {-f1 / lam:.2f} ; poids du coût du capital = {-f2 / lam:.2f} ; somme = {-(f1 + f2) / lam:.2f} (homogénéité : 1)")
# 3. cible homogène imposée avec θ = part moyenne du travail dans la VA (frontière de prix de facteurs)
theta = float((p.clu_net * p.q / p.va_cp)[(p.annee >= 1997) & (p.annee <= 2019)].median())
p["ecm_k"] = p.lpva_1 - theta * p.lclu_n_1 - (1 - theta) * p.lcku_1
r2 = est(["dlclu_n", "dlq", "tucd", "ecm_k"]); show(f"K2 : cible homogène θ = part du travail ({theta:.2f})", r2, ["dlclu_n", "dlq", "ecm_k"])
# 4. transmission propre des subventions sur salaires (CICE) : Δln csu_net = Δln csu_brut + Δln(1 − s)
r3 = est(["dlclu_b", "dlsub", "dlq", "tucd", "ecm_v09"]); show("T1 : CSU brut et subvention séparés", r3, ["dlclu_b", "dlsub", "ecm_v09"])
print(f"   test d'égalité des transmissions (brut = subvention) : p = {r3.t_test('dlclu_b - dlsub = 0').pvalue:.3f}")
# 5. hétérogénéité : tension sur les capacités, exposition, niveau de marge
p["dlclu_tuc"] = p.dlclu_n * p.tucd; p["dlclu_exp"] = p.dlclu_n * p.expose; p["dlclu_marge"] = p.dlclu_n * (p.marge_1 - p.marge_1.mean())
r4 = est(["dlclu_n", "dlclu_tuc", "dlclu_exp", "dlclu_marge", "dlq", "tucd", "ecm_v09"])
show("T2 : transmission selon tension, exposition, marge initiale", r4, ["dlclu_n", "dlclu_tuc", "dlclu_exp", "dlclu_marge", "ecm_v09"])
# 6. asymétrie hausse / baisse du CSU
p["dlclu_h"] = p.dlclu_n.clip(lower=0); p["dlclu_b2"] = p.dlclu_n.clip(upper=0)
r5 = est(["dlclu_h", "dlclu_b2", "dlq", "tucd", "ecm_v09"]); show("T3 : hausses / baisses du CSU", r5, ["dlclu_h", "dlclu_b2", "ecm_v09"])
print(f"   test d'égalité hausse = baisse : p = {r5.t_test('dlclu_h - dlclu_b2 = 0').pvalue:.3f}")
p.to_pickle(H.parent / "b4_panel.pkl")
# 7. frontière des prix de facteurs avec coût du capital à taux réel normatif constant (pas de canal de taux)
out = []
for b, d in p.groupby("branche"):
    d = d.copy()
    rstar = float((d.r - d.pi_e).loc[(d.annee >= 1997) & (d.annee <= 2019)].mean())
    d["lcku_s"] = np.log(d.pi * (rstar + d.delta) * d.k.shift(1) / d.q)
    d["lcku_s_1"] = d.lcku_s.shift(1)
    d["theta_b"] = float((d.clu_net * d.q / d.va_cp).loc[(d.annee >= 1997) & (d.annee <= 2019)].median())
    out.append(d)
p = pd.concat(out)
r6 = est(["dlclu_n", "dlq", "tucd", "lpva_1", "lclu_n_1", "lcku_s_1"], data=p)
lam, f1, f2 = r6.params["lpva_1"], r6.params["lclu_n_1"], r6.params["lcku_s_1"]
show("K3 : cible libre, coût du capital à taux réel normatif", r6, ["dlclu_n", "lpva_1", "lclu_n_1", "lcku_s_1"])
print(f"   poids CSU = {-f1 / lam:.2f} ; poids coût du capital = {-f2 / lam:.2f} ; somme = {-(f1 + f2) / lam:.2f}")
p["ecm_f"] = p.lpva_1 - p.theta_b * p.lclu_n_1 - (1 - p.theta_b) * p.lcku_s_1
r7 = est(["dlclu_n", "dlq", "tucd", "ecm_f"], data=p); show("K4 : frontière homogène, θ = part du travail de la branche, taux normatif", r7, ["dlclu_n", "dlq", "ecm_f"])
# hors échantillon : simulation dynamique des prix de VA 2021-2024 (CSU, volumes, coût du capital observés)
def sim(r, ecm_fun, a, f):
    L = []
    for b in S.BRANCHES:
        d = p[p.branche == b].set_index("annee")
        if d.loc[a - 1:f, ["dlpva", "dlclu_n", "dlq"]].isna().any().any():
            continue
        c = r.params["const"] + r.params.get(f"fe_{b}", 0.0); lp = float(d.lpva[a - 1])
        for t in range(a, f + 1):
            dl = c + r.params["dlclu_n"] * d.dlclu_n[t] + r.params["dlq"] * d.dlq[t] + r.params["tucd"] * d.tucd[t] + ecm_fun(r, d, t, lp)
            L.append((float(d.va_cp[a - 1]), dl - d.dlpva[t], b)); lp += dl
    W = sum(x[0] for x in L)
    return 100 * np.sqrt(sum(w * e ** 2 for w, e, b in L) / W), 100 * np.sqrt(sum(w * e ** 2 for w, e, b in L if b not in ("B", "C19", "D")) / sum(w for w, e, b in L if b not in ("B", "C19", "D")))
for nom, r, fn in (("V0 (v0.9)", r0, lambda r, d, t, lp: r.params["ecm_v09"] * (lp - d.lclu_n[t - 1])),
                   ("K4 frontière", r7, lambda r, d, t, lp: r.params["ecm_f"] * (lp - d.theta_b[t] * d.lclu_n[t - 1] - (1 - d.theta_b[t]) * d.lcku_s[t - 1]))):
    print(f"RMSE Δln pva (pts), simulation dynamique : 2014-2016 {sim(r, fn, 2014, 2016)[0]:.2f} (hors énergie {sim(r, fn, 2014, 2016)[1]:.2f}) ; 2021-2024 {sim(r, fn, 2021, 2024)[0]:.2f} (hors énergie {sim(r, fn, 2021, 2024)[1]:.2f}) — {nom}")
