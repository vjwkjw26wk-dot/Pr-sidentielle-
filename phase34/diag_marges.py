"""Diagnostic du bloc prix : marge observée (ln prix de VA − ln coût salarial unitaire), par grand secteur, 2008-2024,
et transmission des prix des consommations intermédiaires (prix de production vs prix de VA)."""
import sys, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m7_series as S
import m8_modele as M
p = S.panel_branches()
sv = M.taux_subvention_salaires()
p = p[(p.annee >= 2008) & (p.annee <= 2024)].copy()
p["cout_net"] = p.wb * (1 - p.annee.map(sv).fillna(0))
grp = {"industrie hors énergie": [b for b in S.INDUSTRIE if b not in ("C19", "D", "B")], "énergie (B, C19, D)": ["B", "C19", "D"],
       "construction": ["F"], "services marchands": ["G", "H", "I", "J", "K", "M_N", "R-U"], "agriculture": ["A"]}
L = {}
for nom, bs in list(grp.items()) + [("ensemble marchand", S.BRANCHES)]:
    d = p[p.branche.isin(bs)].groupby("annee")[["va_cp", "q", "wb", "cout_net", "y_cp", "y"]].sum()
    pva, clu, clun = d.va_cp / d.q, d.wb / d.q, d.cout_net / d.q
    py = d.y_cp / d.y
    L[(nom, "marge brute ln(pva/CSU) Δ")] = 100 * np.log(pva / clu).diff()
    L[(nom, "marge nette CICE Δ")] = 100 * np.log(pva / clun).diff()
    L[(nom, "prix production Δ%")] = 100 * np.log(py).diff()
    L[(nom, "prix VA Δ%")] = 100 * np.log(pva).diff()
df = pd.DataFrame(L).T.loc[:, 2012:2024].round(1)
print(df.to_string())
