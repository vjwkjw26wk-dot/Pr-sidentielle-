"""A.2 — Diagnostic de l'ancrage nominal : choc salarial temporaire (+2 % en 2011, sans déplacement de la cible),
trajectoires 2011-2025 (exogènes observées, écart à la base), selon la fermeture, la pente de Phillips et la
spécification. Si l'économie est ancrée, l'écart de niveau de prix doit se résorber (ou se stabiliser) et l'écart
d'inflation revenir à zéro."""
import pathlib, sys
H = pathlib.Path(__file__).resolve()
sys.path[:0] = [str(H.parents[2] / "phase34"), str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import lab, m7_equations as E, m8_modele as M
from lab import V09
CAND_A = {**V09, "prix_va": "ci_hausse", "indexation_retard": 0.17}
ANS = (2011, 2013, 2015, 2018, 2020, 2025)

def choc_w(mod, ex):
    """Choc ADDITIF : la base contient déjà, en 2019, la bascule CICE → allègements (choc de salaire négatif)."""
    base = ex.choc_salaire if ex.choc_salaire is not None else pd.Series(0.0, index=range(2011, 2026))
    ex.choc_salaire = base.add(pd.Series({t: (0.02 if t == 2011 else 0.0) for t in range(2011, 2026)}), fill_value=0.0)

def trajectoires(spec, clos="v08", phillips=None):
    ph0 = E.PHILLIPS
    if phillips is not None:
        E.PHILLIPS = phillips
    try:
        b = lab.run(2010, 2025, clos, spec, retour=True)[1]
        v = lab.run(2010, 2025, clos, spec, exp_mod=choc_w, retour=True)[1]
    finally:
        E.PHILLIPS = ph0
    out = {}
    for t in ANS:
        out[t] = {"niveau prix conso (%)": 100 * (v.pc[t] / b.pc[t] - 1),
                  "inflation (pt)": 100 * (np.log(v.pc[t] / b.pc[t]) - (np.log(v.pc[t - 1] / b.pc[t - 1]) if t - 1 in v.index else 0.0)),
                  "salaire (%)": 100 * (v.salaire[t] / b.salaire[t] - 1),
                  "prix VA (%)": 100 * (v.pva_m[t] / b.pva_m[t] - 1),
                  "PIB (%)": 100 * (v.pib[t] / b.pib[t] - 1), "chômage (pt)": v.chomage[t] - b.chomage[t],
                  "exportations (%)": 100 * (v.x[t] / b.x[t] - 1), "fermeture Z (% PIB)": 100 * (v.supplement_demande_fermeture[t] - b.supplement_demande_fermeture[t]) / b.pib[t]}
    return pd.DataFrame(out)

cas = {"v0.9, fermeture v0.8": (V09, "v08", None), "v0.9, sans fermeture (demande)": (V09, "demande", None),
       "v0.9, Phillips ×3": (V09, "v08", 3 * E.PHILLIPS), "v0.9, sans fermeture, Phillips ×3": (V09, "demande", 3 * E.PHILLIPS),
       "candidate A, fermeture v0.8": (CAND_A, "v08", None)}
res = {}
for nom, (spec, clos, ph) in cas.items():
    res[nom] = trajectoires(spec, clos, ph)
    print(f"\n=== {nom} (Phillips = {ph if ph is not None else E.PHILLIPS})")
    print(res[nom].round(2).to_string())
pd.concat(res).to_csv(H.parent / "b1_ancrage.csv")
