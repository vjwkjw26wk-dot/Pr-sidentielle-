"""Phase 4.2, chantier A : équation de prix de VA étendue aux coûts intermédiaires (V0-V3), estimation 1998-2019,
simulation dynamique 2014-2016 (dans l'échantillon) et 2021-2024 (hors échantillon), par grand secteur."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m18_prix as P, m7_series as S
d = P.panel_va()
GR = {"industrie hors énergie": [b for b in S.INDUSTRIE if b not in P.ENERGIE], "énergie": P.ENERGIE,
      "construction": ["F"], "services marchands": [b for b in S.BRANCHES if b not in S.INDUSTRIE + ["F", "A"]]}
rows = {}
for spec in P.VA_SPECS:
    r = P.estimer_va(d, spec)
    row = {k: f"{r.params[k]:.3f} ({r.bse[k]:.3f})" for k in ["dlclu", "dlq", "tucd", "ecm_1"] + P.VA_SPECS[spec]}
    row["R2"] = round(r.rsquared, 3)
    for a, f in ((2014, 2016), (2021, 2024)):
        L = []
        for b in S.BRANCHES:
            x = d[d.branche == b].set_index("annee")
            cols = ["dlpva", "dlclu", "dlq"] + P.VA_SPECS[spec]
            if x.loc[a:f, cols].isna().any().any():
                continue
            s = P.simuler_va(d, r, spec, b, a, f)
            w = float(x.va_cp[a - 1])
            L += [(w, float(s[t] - x.dlpva[t]), b, t) for t in range(a, f + 1)]
        W = sum(z[0] for z in L)
        row[f"RMSE {a}-{f}"] = round(100 * np.sqrt(sum(w * e ** 2 for w, e, _, _ in L) / W), 2)
        row[f"RMSE {a}-{f} hors énergie"] = round(100 * np.sqrt(sum(w * e ** 2 for w, e, b, _ in L if b not in P.ENERGIE) / sum(w for w, e, b, _ in L if b not in P.ENERGIE)), 2)
        row[f"biais {a}-{f}"] = round(100 * sum(w * e for w, e, _, _ in L) / W, 2)
        for g, bs in GR.items():
            for t in ((2015,) if a == 2014 else (2022, 2023)):
                sel = [(w, e) for w, e, b, tt in L if b in bs and tt == t]
                if sel:
                    row[f"{g} {t}"] = round(100 * sum(w * e for w, e in sel) / sum(w for w, e in sel), 2)
    rows[spec] = row
pd.set_option("display.width", 250)
df = pd.DataFrame(rows)
print(df.to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "a3_prix_va_ci.csv")
