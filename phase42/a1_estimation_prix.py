"""Phase 4.2, chantier A : estimation et comparaison des spécifications de prix de production (M18)."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m18_prix as P
p = P.panel_prix()
res = P.comparer(p)
rows = {}
for spec, (r, row) in res.items():
    rows[spec] = {k: (f"{v[0]:.3f} ({v[1]:.3f})" if isinstance(v, tuple) else (round(v, 3) if v == v else "")) for k, v in row.items()}
df = pd.DataFrame(rows).T
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(df.T.to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "a1_specifications_prix.csv")
# diagnostic des épisodes : marge observée par grand secteur
g = p[p.annee.between(2012, 2024)].groupby(["energie", "annee"]).apply(lambda d: np.average(d.marge.diff().fillna(0), weights=d.y_cp))
