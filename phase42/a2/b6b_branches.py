import pathlib, sys
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parent), str(H.parents[2] / "phase34"), str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import lab
from lab import V09
from b5_chocs_ancrage import choc
mod, ex, ans = lab.construire(2010, 2025, "v08", V09)
b = mod.simuler(ans, ex); Hb = {k: {v: dict(d) for v, d in vv.items()} for k, vv in mod.H.items()}
choc("taux d'intérêt +1 pt permanent")(mod, ex)
v = mod.simuler(ans, ex); Hv = mod.H
rows = {}
for br in mod.BR:
    rows[br] = {f"pva {t}": 100 * np.log(Hv[br]["pva"][t] / Hb[br]["pva"][t]) for t in (2021, 2023, 2024, 2025)}
    rows[br].update({f"k {t}": 100 * np.log(Hv[br]["k"][t] / Hb[br]["k"][t]) for t in (2023, 2025)})
    rows[br].update({f"n {t}": 100 * np.log(Hv[br]["n"][t] / Hb[br]["n"][t]) for t in (2023, 2025)})
    rows[br]["tuc_B"] = mod.tuc_B.get(br, np.nan)
print(pd.DataFrame(rows).T.round(1).sort_values("pva 2025").to_string())
