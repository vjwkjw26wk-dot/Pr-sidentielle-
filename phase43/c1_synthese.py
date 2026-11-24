"""Synthèse du chantier C (niveaux 2 et 3) : erreur absolue moyenne par horizon, variable et méthode."""
import json, pathlib, sys
import numpy as np, pandas as pd
f = pathlib.Path(__file__).parent / "resultats" / "c1_ex_ante_v0.9_T1_P4.json"
r = json.loads(f.read_text())
rows = []
for k, v in r.items():
    meth, B, mode = k.split("|")
    for h, d in v.items():
        for var, e in d.items():
            rows.append(dict(methode=f"{meth} — {mode}", origine=int(B), h=int(h), var=var, err=e))
df = pd.DataFrame(rows)
pd.set_option("display.width", 250)
for per, sel in (("origines 2010-2016 (avant crise sanitaire)", df.origine < 2020), ("origine 2021 (choc énergétique)", df.origine == 2021)):
    print(f"\n=== Erreur absolue moyenne, {per}")
    t = df[sel].assign(abs=lambda x: x.err.abs()).pivot_table(index=["var", "h"], columns="methode", values="abs", aggfunc="mean")
    print(t.round(2).to_string())
    print(f"\n=== Biais moyen (simulé − observé), {per}")
    t = df[sel].pivot_table(index=["var", "h"], columns="methode", values="err", aggfunc="mean")
    print(t.round(2).to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "c1_erreurs.csv", index=False)
