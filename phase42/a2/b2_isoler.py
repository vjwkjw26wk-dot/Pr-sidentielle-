"""A.2 — Isoler la boucle responsable de la dérive : choc salarial temporaire (+2 % en 2011), base 2010-2025,
avec gel successif des boucles (emploi, consommation, fermeture) ; suivi annuel des variables nominales et réelles."""
import copy, pathlib, sys
H = pathlib.Path(__file__).resolve()
sys.path[:0] = [str(H.parents[2] / "phase34"), str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import lab, m8_modele as M
from lab import V09
mod, ex, ans = lab.construire(2010, 2025, "v08", V09)
b = mod.simuler(ans, ex)
g = mod.trajectoires_gel(ans)
def var(gel):
    e = copy.deepcopy(ex)
    e.choc_salaire = pd.Series({t: (0.02 if t == 2011 else 0.0) for t in ans})
    e.gel = {k: g[k] for k in gel} or None
    return mod.simuler(ans, e)
rows = {}
for nom, gel in (("complet", []), ("emploi gelé", ["emploi"]), ("emploi + consommation + fermeture gelés", ["emploi", "C", "Z"])):
    v = var(gel)
    ps = np.log(v.salaire / b.salaire) - np.log(v.pva_m / b.pva_m)            # part salariale (productivité inchangée si emploi gelé)
    for t in ans:
        rows[(nom, t)] = {"prix conso (%)": 100 * np.log(v.pc[t] / b.pc[t]), "prix VA (%)": 100 * np.log(v.pva_m[t] / b.pva_m[t]),
                          "salaire (%)": 100 * np.log(v.salaire[t] / b.salaire[t]), "salaire − prix VA (%)": 100 * ps[t],
                          "emploi (milliers)": v.emploi[t] - b.emploi[t], "taux de marge (pt)": v.taux_marge[t] - b.taux_marge[t]}
df = pd.DataFrame(rows).T
pd.set_option("display.max_rows", 100)
print(df.round(2).to_string())
