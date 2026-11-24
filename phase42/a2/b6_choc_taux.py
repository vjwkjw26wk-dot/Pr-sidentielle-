"""A.2 — Diagnostic de l'instabilité du choc de taux permanent (+1 point en 2011), v0.9, trajectoire annuelle."""
import pathlib, sys
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parent), str(H.parents[2] / "phase34"), str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import lab
from lab import V09
from b5_chocs_ancrage import choc
for nom, spec in (("v0.9 sans effet de tension sur les prix", {**V09, "tension_prix": "aucune"}),
                  ("C1 frontière sans effet de tension", {**V09, "prix_va": "frontiere", "tension_prix": "aucune"})):
    b = lab.run(2010, 2025, "v08", spec, retour=True)[1]
    v = lab.run(2010, 2025, "v08", spec, exp_mod=choc("taux d'intérêt +1 pt permanent"), retour=True)[1]
    T = pd.DataFrame({"PIB (%)": 100 * np.log(v.pib / b.pib), "prix (%)": 100 * np.log(v.pc / b.pc), "salaire (%)": 100 * np.log(v.salaire / b.salaire),
                      "invest. (%)": 100 * np.log(v.fbcf / b.fbcf), "capital (%)": 100 * np.log(v.capital_marchand / b.capital_marchand),
                      "chômage (pt)": v.chomage - b.chomage, "écart prod. (pt)": v.ecart_production - b.ecart_production,
                      "fermeture Z (%PIB)": 100 * (v.supplement_demande_fermeture - b.supplement_demande_fermeture) / b.pib,
                      "dette (pt)": v.dette_pib - b.dette_pib, "intérêts (Md€)": (v.interets - b.interets) / 1e3})
    print(f"\n=== {nom}\n" + T.round(2).to_string())
