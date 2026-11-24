"""M18 — Formation des prix de production et des marges par branche (phase 4.2, chantier A).

Problème (diagnostic de la phase 3.4) : dans M8 v0.9 les prix de production sont le coût total recalculé à chaque
itération par le système de Leontief, p = (pm·Am + pva·av)(I − Ad − T)⁻¹, et le prix de la VA suit le coût salarial
unitaire. Toute variation de coût intermédiaire passe donc instantanément et intégralement dans le prix de production ;
la marge ne peut pas l'absorber. Les comptes montrent le contraire (2015 : prix de VA de l'industrie +3,2 % pour des prix
de production +0,8 % ; 2023 : marge industrielle +7,5 points).

Spécification (prix de production par branche, « mark-up » sur coût variable unitaire, Mésange-like) :
    coût variable unitaire (indice de Divisia, part de l'année précédente) :
        Δln cv = w_ci Δln p_ci + (1 − w_ci) Δln cl_y ,  w_ci = CI / (CI + coût du travail), en valeur, t − 1
        p_ci : prix des consommations intermédiaires (CI = P1 − B1G, aux prix courants et de l'année précédente)
        cl_y : coût du travail par unité de production (rémunérations nettes des subventions sur salaires, non-salariés
               imputés au coût horaire salarié, divisées par la production en volume)
    Δln py = c_b + a_ci·w_ci·Δln p_ci + a_ci1·w_ci·Δln p_ci,−1 + a_l·(1 − w_ci)·Δln cl_y + γ·TUC + λ [ln py − ln cv]_{−1}
Homogénéité de long terme (prix ∝ coût variable) imposée ; marge de long terme constante par branche (effet fixe).
Le prix de la VA s'en déduit comptablement : pva·q = py·y − p_ci·ci ; la marge (EBE) absorbe les chocs de coûts
transmis lentement.

Données : Eurostat nama_10_a64 (P1, B1G en CP_MEUR, CLV15_MEUR, PYP_MEUR ; D1), nama_10_a64_e (heures), comme M7.
Les prix des CI sont exacts (rapport valeur courante / valeur aux prix de l'année précédente, chaîné).
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
import statsmodels.api as sm

import m7_series as S

RACINE = pathlib.Path(__file__).resolve().parents[1]
ENERGIE = ["B", "C19", "D"]


def panel_prix(net_subventions=True) -> pd.DataFrame:
    """Panel branche × année : prix de production, des CI, coût du travail par unité de production, parts de coût."""
    from telechargement import jsonstat_dict
    a = pd.Series(jsonstat_dict(json.loads((RACINE / "data" / "raw" / "eurostat_nama_10_a64_FR.json").read_text())))
    g = lambda u, b, i, t: float(a.get((u, b, i, str(t)), np.nan))  # noqa: E731
    p = S.panel_branches()
    p["y_pyp"] = [g("PYP_MEUR", b, "P1", t) for b, t in zip(p.branche, p.annee)]
    p["ci_cp"] = p.y_cp - p.va_cp
    p["ci_pyp"] = p.y_pyp - p.va_pyp
    sv = 0.0
    if net_subventions:
        import m8_modele as M8
        s_ = M8.taux_subvention_salaires()
        sv = p.annee.map(s_).fillna(0.0)
    p["cout_l"] = p.wb * (1 - sv) * p.h / p.hs            # coût du travail, non-salariés imputés
    p = p.sort_values(["branche", "annee"]).reset_index(drop=True)
    out = []
    for b, d in p.groupby("branche"):
        d = d.copy()
        d["dlpy"] = np.log(d.y_cp / d.y_pyp)               # croissance exacte du prix de production
        d["dlpci"] = np.log(d.ci_cp / d.ci_pyp)            # croissance exacte du prix des CI
        d["lpy"] = d.dlpy.fillna(0).cumsum()
        d["lpci"] = d.dlpci.fillna(0).cumsum()
        d["lcly"] = np.log(d.cout_l / d.y)                 # coût du travail par unité de production (volume)
        d["dlcly"] = d.lcly.diff()
        d["w_ci"] = (d.ci_cp / (d.ci_cp + d.cout_l)).shift(1)
        d["dlcv"] = d.w_ci * d.dlpci + (1 - d.w_ci) * d.dlcly
        d["lcv"] = d.dlcv.fillna(0).cumsum()
        d["marge"] = d.lpy - d.lcv                         # ln(prix / coût variable), à une constante près
        d["dlpci_1"] = d.dlpci.shift(1)
        d["marge_1"] = d.marge.shift(1)
        d["s_ci"] = d.ci_cp / d.y_cp
        out.append(d)
    p = pd.concat(out).reset_index(drop=True)
    T = S.tuc()
    moy = T.loc[1995:2019].mean()
    p["tucd"] = [float(T.loc[t, S.TUC_BRANCHE[b]] - moy[S.TUC_BRANCHE[b]]) if (b in S.TUC_BRANCHE and t in T.index) else 0.0
                 for b, t in zip(p.branche, p.annee)]
    p["energie"] = p.branche.isin(ENERGIE).astype(float)
    return p


def _poids(d):
    return d.groupby("annee").y_cp.transform(lambda s: s / s.sum())


SPECS = {
    "P1 correction d'erreur commune": ["x_ci", "x_ci1", "x_l", "ecm"],
    "P2 + transmission propre à l'énergie": ["x_ci", "x_ci1", "x_l", "ecm", "x_ci_en", "x_ci1_en", "ecm_en"],
    "P3 + asymétrie hausse / baisse des CI": ["x_ci_h", "x_ci_b", "x_ci1", "x_l", "ecm"],
    "P4 + tension sur les capacités": ["x_ci", "x_ci1", "x_l", "ecm", "tucd"],
}


def regresseurs(d):
    X = pd.DataFrame(index=d.index)
    X["x_ci"] = d.w_ci * d.dlpci
    X["x_ci1"] = d.w_ci * d.dlpci_1
    X["x_l"] = (1 - d.w_ci) * d.dlcly
    X["ecm"] = d.marge_1
    X["x_ci_en"] = X.x_ci * d.energie
    X["x_ci1_en"] = X.x_ci1 * d.energie
    X["ecm_en"] = X.ecm * d.energie
    X["x_ci_h"] = X.x_ci.clip(lower=0)
    X["x_ci_b"] = X.x_ci.clip(upper=0)
    X["tucd"] = d.tucd / 100
    return X


def estimer(p, spec, debut=1998, fin=2019):
    d = p[(p.annee >= debut) & (p.annee <= fin)].copy()
    X = regresseurs(d)[SPECS[spec]]
    X = pd.concat([X, pd.get_dummies(d.branche, prefix="fe", drop_first=True, dtype=float)], axis=1)
    ok = X.notna().all(axis=1) & d.dlpy.notna()
    r = sm.WLS(d.dlpy[ok], sm.add_constant(X[ok]), weights=_poids(d)[ok]).fit(cov_type="cluster", cov_kwds={"groups": d.annee[ok]})
    return r


def simuler_branche(p, r, spec, b, debut, fin):
    """Simulation dynamique du prix de production d'une branche (coûts observés, prix et marge simulés)."""
    d = p[p.branche == b].set_index("annee")
    fe = r.params.get(f"fe_{b}", 0.0) + r.params["const"]
    lpy = {debut - 1: float(d.lpy[debut - 1])}
    for t in range(debut, fin + 1):
        row = d.loc[[t]].copy()
        row["marge_1"] = lpy[t - 1] - float(d.lcv[t - 1])
        X = regresseurs(row.reset_index())[SPECS[spec]].iloc[0]
        dl = fe + sum(r.params[k] * X[k] for k in SPECS[spec])
        lpy[t] = lpy[t - 1] + dl
    return pd.Series(lpy)


def comparer(p, debut_est=1998, fin_est=2019, episodes=((2014, 2016), (2021, 2024))):
    """Ajustement, simulation dynamique hors échantillon des prix de production et de la marge implicite."""
    res = {}
    for spec in SPECS:
        r = estimer(p, spec, debut_est, fin_est)
        row = {k: (float(r.params[k]), float(r.bse[k])) for k in SPECS[spec]}
        lam = r.params["ecm"]
        row["demi-vie de l'écart de marge (ans)"] = float(np.log(0.5) / np.log(1 + lam)) if -1 < lam < 0 else np.nan
        row["R2"] = float(r.rsquared)
        for a, f in episodes:
            err_p, err_m = [], []
            for b in S.BRANCHES:
                d = p[p.branche == b].set_index("annee")
                if d.loc[a - 1:f, ["dlpy", "dlpci", "dlcly"]].isna().any().any():
                    continue
                s = simuler_branche(p, r, spec, b, a, f)
                w = float(d.y_cp[a - 1])
                for t in range(a, f + 1):
                    err_p.append((w, (s[t] - s[t - 1]) - float(d.dlpy[t])))
                    # marge implicite : variation du ln(py/cv) simulée vs observée
                    err_m.append((w, (s[t] - float(d.lcv[t])) - (s[t - 1] - float(d.lcv[t - 1])) - (float(d.marge[t]) - float(d.marge[t - 1]))))
            W = sum(x[0] for x in err_p)
            row[f"RMSE Δln py {a}-{f} (pts)"] = 100 * float(np.sqrt(sum(w * e ** 2 for w, e in err_p) / W))
            row[f"biais Δln py {a}-{f} (pts)"] = 100 * float(sum(w * e for w, e in err_p) / W)
        res[spec] = (r, row)
    # P0 : transmission instantanée intégrale (architecture v0.9) : Δln py = Δln cv + constante de branche
    row = {}
    for a, f in episodes:
        err = []
        for b in S.BRANCHES:
            d = p[p.branche == b].set_index("annee")
            if d.loc[a - 1:f, ["dlpy", "dlcv"]].isna().any().any():
                continue
            c = float((d.dlpy - d.dlcv).loc[debut_est:fin_est].mean())
            w = float(d.y_cp[a - 1])
            err += [(w, c + float(d.dlcv[t]) - float(d.dlpy[t])) for t in range(a, f + 1)]
        W = sum(x[0] for x in err)
        row[f"RMSE Δln py {a}-{f} (pts)"] = 100 * float(np.sqrt(sum(w * e ** 2 for w, e in err) / W))
        row[f"biais Δln py {a}-{f} (pts)"] = 100 * float(sum(w * e for w, e in err) / W)
    res["P0 transmission instantanée (v0.9)"] = (None, row)
    return res


def pva_implicite(d, lpy_sim):
    """Prix de la VA impliqué par un prix de production simulé : pva·q = py·y − p_ci·ci (volumes et prix des CI
    observés). Renvoie Δln pva par année."""
    py_obs = np.exp(d.lpy)
    pci = np.exp(d.lpci)
    y_vol = d.y_cp / py_obs                 # volume de production à l'échelle de l'indice py
    ci_vol = d.ci_cp / pci
    out = {}
    for t in lpy_sim.index[1:]:
        va_t = np.exp(lpy_sim[t]) * y_vol[t] - pci[t] * ci_vol[t]
        va_1 = np.exp(lpy_sim[t - 1]) * y_vol[t - 1] - pci[t - 1] * ci_vol[t - 1]
        out[t] = np.log(va_t / d.q[t]) - np.log(va_1 / d.q[t - 1])
    return pd.Series(out)


def simuler_pva_v09(p_m7, r, b, debut, fin):
    """Simulation dynamique de l'équation de prix de VA de la v0.9 (coûts salariaux unitaires, volumes et TUC observés)."""
    import m7_equations as E
    d = p_m7[p_m7.branche == b].set_index("annee")
    T = S.tuc(); moy = T.loc[1995:2019].mean()
    tucd = lambda t: float(T.loc[t, S.TUC_BRANCHE[b]] - moy[S.TUC_BRANCHE[b]]) if (b in S.TUC_BRANCHE and t in T.index) else 0.0  # noqa: E731
    c = r.params["const"] + r.params.get(f"fe_{b}", 0.0)
    lp = {debut - 1: float(np.log(d.pva[debut - 1]))}
    lclu = np.log(d.clu)
    for t in range(debut, fin + 1):
        dl = (c + r.params["dlclu"] * (lclu[t] - lclu[t - 1]) + r.params["dlq"] * np.log(d.q[t] / d.q[t - 1])
              + r.params.get("tucd", 0.0) * tucd(t) + r.params["ecm_1"] * (lp[t - 1] - lclu[t - 1]))
        lp[t] = lp[t - 1] + dl
    s = pd.Series(lp)
    return s.diff().dropna()


# ---------------------------------------------------------------------------------------------------------------
# Extension de l'équation de prix de VA (M7) aux coûts intermédiaires
#   Δln pva = a_b + α0 Δln clu + α1 Δln q + γ TUC + λ [ln pva − ln clu]_{−1}
#             + β⁺ L_{−1}·max(Δln p_ci − Δln py*, 0)... (variantes ci-dessous)
#   L = CI / VA (levier, t − 1) : une marge proportionnelle au coût total, ou une transmission incomplète des coûts
#   intermédiaires au prix de production, se traduit en prix de VA avec ce levier.
# ---------------------------------------------------------------------------------------------------------------
VA_SPECS = {
    "V0 équation v0.9": [],
    "V1 + coûts intermédiaires (linéaire)": ["z_ci"],
    "V2 + hausse / baisse des coûts intermédiaires": ["z_ci_h", "z_ci_b"],
    "V3 = V2 + effet retardé": ["z_ci_h", "z_ci_b", "z_ci_1"],
    "V4 hausses seules": ["z_ci_h"],
}


def panel_va(p=None, pm7=None):
    import m7_equations as E
    pm7 = S.panel_branches() if pm7 is None else pm7
    d = E._prep_panel(pm7, 1995, 2025)
    p = panel_prix() if p is None else p
    x = p.set_index(["branche", "annee"])
    k = list(zip(d.branche, d.annee))
    lev = (x.ci_cp / x.va_cp).groupby(level=0).shift(1)
    dl = x.dlpci
    d["z_ci"] = [float(lev.get(i, np.nan) * dl.get(i, np.nan)) for i in k]
    d["z_ci_h"] = d.z_ci.clip(lower=0)
    d["z_ci_b"] = d.z_ci.clip(upper=0)
    d["z_ci_1"] = d.groupby("branche").z_ci.shift(1)
    import m7_equations as E2
    d["tucd"] = E2.tension_capacites(d)
    return d


def estimer_va(d, spec, debut=1998, fin=2019):
    dd = d[(d.annee >= debut) & (d.annee <= fin)]
    X = pd.DataFrame({"dlclu": dd.dlclu, "dlq": dd.dlq, "tucd": dd.tucd, "ecm_1": dd.lpva_1 - dd.lclu_1})
    for c in VA_SPECS[spec]:
        X[c] = dd[c]
    X = pd.concat([X, pd.get_dummies(dd.branche, prefix="fe", drop_first=True, dtype=float)], axis=1)
    ok = X.notna().all(axis=1) & dd.dlpva.notna()
    w = dd.groupby("annee").va_cp.transform(lambda s: s / s.sum())
    return sm.WLS(dd.dlpva[ok], sm.add_constant(X[ok]), weights=w[ok]).fit(cov_type="cluster", cov_kwds={"groups": dd.annee[ok]})


def simuler_va(d, r, spec, b, debut, fin):
    x = d[d.branche == b].set_index("annee")
    c = r.params["const"] + r.params.get(f"fe_{b}", 0.0)
    lp = {debut - 1: float(x.lpva[debut - 1])}
    for t in range(debut, fin + 1):
        dl = (c + r.params["dlclu"] * float(x.dlclu[t]) + r.params["dlq"] * float(x.dlq[t]) + r.params["tucd"] * float(x.tucd[t])
              + r.params["ecm_1"] * (lp[t - 1] - float(x.lclu[t - 1])) + sum(r.params[k] * float(x[k][t]) for k in VA_SPECS[spec]))
        lp[t] = lp[t - 1] + dl
    return pd.Series(lp).diff().dropna()
