"""Phase 4.2, chantier A : équation de salaires (W0-W3), estimation 1998-2019, simulation dynamique hors échantillon."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m19_salaires as W
d = W.donnees()
# 1. la règle légale approchée reproduit-elle le SMIC ?
err = {t: 100 * (W.regle_smic(d, t, d.dlpc[t], d.dlw[t - 1], d.dlpc[t - 1]) - d.dlsmic[t]) for t in range(1998, 2025)}
print("Règle du SMIC (sans coups de pouce), erreur annuelle (pts) :", {t: round(v, 1) for t, v in err.items()})
rows = {}
for spec in W.SPECS_W:
    r = W.estimer(d, spec)
    row = {k: f"{r.params[k]:.3f} ({r.bse[k]:.3f})" for k in r.params.index}
    row["R2"] = round(r.rsquared, 3)
    if "tdc_1" in r.params:
        row["poids des prix conso dans la cible (−tdc/ecm)"] = round(float(-r.params["tdc_1"] / r.params["ecm_1"]), 2)
    for endo in ((False, True) if "SMIC" in spec else (False,)):
        lw, ls = W.simuler(d, r, spec, 2021, 2024, smic_endogene=endo)
        tag = " (SMIC endogène)" if endo else (" (SMIC observé)" if "SMIC" in spec else "")
        sim = 100 * lw.diff().loc[2022:2024]
        for t in (2022, 2023, 2024):
            row[f"Δln w {t}{tag}"] = round(float(sim[t]), 2)
        row[f"erreur de niveau 2024{tag} (%)"] = round(100 * float(lw[2024] - d.lw[2024]), 2)
        if endo:
            row["SMIC simulé 2022-24 (%)"] = [round(float(x), 1) for x in 100 * ls.diff().loc[2022:2024]]
    # dans l'échantillon : 2015-2019
    lw, _ = W.simuler(d, r, spec, 2015, 2019)
    row["RMSE Δln w 2015-2019 (pts)"] = round(float(100 * np.sqrt(((lw.diff() - d.dlw).loc[2015:2019] ** 2).mean())), 2)
    rows[spec] = row
obs = {f"observé {t}": round(100 * float(d.dlw[t]), 2) for t in (2022, 2023, 2024)}
print("Salaire moyen marchand observé :", obs, " SMIC observé :", [round(100 * float(d.dlsmic[t]), 1) for t in (2022, 2023, 2024)])
pd.set_option("display.width", 250)
df = pd.DataFrame(rows)
print(df.to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "a5_salaires.csv")
