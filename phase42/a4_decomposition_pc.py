"""Phase 4.2, chantier A : décomposition de l'erreur de prix 2021-2025 (backtest v0.9, origine 2021) et 2015-2019."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "phase34"), str(R / "src")]
import numpy as np, pandas as pd
from lab import run, V09
import m7_series as S
for B, fin in ((2021, 2025), (2014, 2019)):
    res, r, mod, o = run(B, fin, "v08", V09, retour=True)
    m = mod.macro
    br = mod.BR
    va = sum(mod.hist[b].va_cp for b in br); q = sum(mod.hist[b].q for b in br)
    wb = sum(mod.hist[b].wb for b in br); ns = sum(mod.hist[b].ns for b in br); h = sum(mod.hist[b].h for b in br); hs = sum(mod.hist[b].hs for b in br)
    obs = pd.DataFrame({"pc": m.p_c, "pm": m.p_m, "px": m.p_x, "pva_m": va / q, "salaire": wb / ns, "clu": wb / hs * h / q})
    sim = pd.DataFrame({"pc": r.pc, "pm": r.pm_agg if "pm_agg" in r else np.nan, "px": r.px, "pva_m": r.pva_m, "salaire": r.salaire})
    T = {}
    for k in ["pc", "pm", "px", "pva_m", "salaire"]:
        if k in sim and sim[k].notna().any():
            so = obs[k] / obs[k][B]; ss = sim[k] / sim[k].iloc[0] * (obs[k][B + 1] / obs[k][B]) if False else sim[k] / obs[k][B]
            T[f"{k} obs (Δ%)"] = 100 * np.log(obs[k]).diff().loc[B + 1:fin]
            T[f"{k} sim (Δ%)"] = 100 * np.log(pd.concat([pd.Series({B: obs[k][B]}), sim[k].loc[B + 1:fin]])).diff().loc[B + 1:fin]
    print(f"\n=== origine {B} : croissances annuelles observées / simulées (%)")
    print(pd.DataFrame(T).round(2).T.to_string())
