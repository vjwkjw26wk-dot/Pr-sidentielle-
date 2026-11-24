"""Phase 4.2, chantier A : prix de VA (marges) implicites des spécifications M18 contre l'équation de prix de VA v0.9,
simulation dynamique branche par branche avec coûts observés ; agrégats industrie hors énergie, énergie, services."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m18_prix as P, m7_equations as E, m7_series as S
p = P.panel_prix()
pm7 = S.panel_branches()
r09 = E.prix_va(pm7, 1997, 2019).res
GR = {"industrie hors énergie": [b for b in S.INDUSTRIE if b not in P.ENERGIE], "énergie": P.ENERGIE,
      "construction": ["F"], "services marchands": [b for b in S.BRANCHES if b not in S.INDUSTRIE + ["F", "A"]]}
specs = ["P0 transmission instantanée (v0.9)", "P1 correction d'erreur commune", "P2 + transmission propre à l'énergie", "P3 + asymétrie hausse / baisse des CI"]
est = {s: P.estimer(p, s) for s in specs[1:]}
rows, err = {}, {}
for a, f in ((2014, 2016), (2021, 2024)):
    for b in S.BRANCHES:
        d = p[p.branche == b].set_index("annee")
        if d.loc[a - 1:f, ["dlpy", "dlpci", "dlcly"]].isna().any().any():
            continue
        obs = np.log(d.va_cp / d.q).diff()
        sims = {"équation de prix de VA v0.9": P.simuler_pva_v09(pm7, r09, b, a, f)}
        c0 = float((d.dlpy - d.dlcv).loc[1998:2019].mean())
        lpy0 = pd.Series({a - 1: float(d.lpy[a - 1])})
        for t in range(a, f + 1):
            lpy0[t] = lpy0[t - 1] + c0 + float(d.dlcv[t])
        sims["P0 transmission instantanée (prix de production)"] = P.pva_implicite(d, lpy0)
        for s in specs[1:]:
            sims[s] = P.pva_implicite(d, P.simuler_branche(p, est[s], s, b, a, f))
        w = float(d.va_cp[a - 1])
        for k, sim in sims.items():
            for t in range(a, f + 1):
                err.setdefault((k, a), []).append((w, float(sim[t] - obs[t]), b, t))
for (k, a), L in err.items():
    W = sum(x[0] for x in L)
    rows.setdefault(k, {})[f"RMSE Δln pva {a}- (pts)"] = round(100 * np.sqrt(sum(w * e ** 2 for w, e, _, _ in L) / W), 2)
    rows[k][f"biais {a}- (pts)"] = round(100 * sum(w * e for w, e, _, _ in L) / W, 2)
    for g, bs in GR.items():
        for t in ((2015,) if a == 2014 else (2022, 2023)):
            sel = [(w, e) for w, e, b, tt in L if b in bs and tt == t]
            if sel:
                rows[k][f"{g} {t}"] = round(100 * sum(w * e for w, e in sel) / sum(w for w, e in sel), 2)
pd.set_option("display.width", 250)
df = pd.DataFrame(rows)
print("Erreur de simulation dynamique du prix de VA (simulé − observé, points de %, pondéré par la VA)\n")
print(df.to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "a2_prix_va_implicite.csv")
