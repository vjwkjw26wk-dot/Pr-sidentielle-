"""Phase 4.3, chantier B : rétrosimulation du compte des sociétés (conditionnelle aux exogènes observés) et comparaison
aux comptes de secteurs ; non-régression des agrégats macro (v0.9 vs v0.9 + compte, T1 vs P4)."""
import pathlib, sys, warnings, json
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lab43 import *  # noqa
import numpy as np, pandas as pd
import m21_societes as S21
d = S21.donnees()
out = {}
for B, fin in ((2010, 2019), (2014, 2019), (2014, 2024), (2019, 2024)):
    for nom in SELECTION_P4:
        res, r, mod, o = run(B, fin, spec=CONFIGS[nom], retour=True)
        out[(B, fin, nom)] = res
        if "ebe_s11" in r:
            ans = [t for t in r.index if t > B]
            cmp = pd.DataFrame({
                "EBE": 100 * (r.ebe_s11 / d.ebe - 1), "intérêts nets (Md€)": (r.interets_s11 - d.int_nets) / 1e3,
                "taux app. (pt)": r.taux_apparent_s11 - d.taux_app, "IS": 100 * (r.is_s11 / d.is_ - 1),
                "dividendes distr.": 100 * (r.dividendes_distribues / d.div_final - 1),
                "épargne": 100 * (r.epargne_s11 / d.b8g - 1), "FBCF": 100 * (r.fbcf_s11 / d.fbcf - 1),
                "B9 (Md€)": (r.capacite_s11 - d.b9) / 1e3, "dette": 100 * (r.dette_s11 / d.dette - 1),
                "autofin. sim/obs": r.taux_autofinancement.round(0).astype(str) + "/" + (100 * d.b8g / d.fbcf).round(0).astype(str),
                "max |identités|": np.maximum(r._identite_b8g.abs(), r._identite_b9.abs())}).loc[ans]
            print(f"\n=== {nom}, origine {B}, fin {fin} : écarts simulé − observé (%, sauf indication)")
            print(cmp.round(1).to_string())
print()
print(table({f"{k[2]} | {k[0]}-{k[1]}": v for k, v in out.items()}, ["pib", "pc", "emploi", "chomage", "dette", "solde", "rmse_pib_g", "rmse_pc_g"]))
pd.DataFrame(out).T.to_csv(pathlib.Path(__file__).parent / "b3_backtests.csv")
