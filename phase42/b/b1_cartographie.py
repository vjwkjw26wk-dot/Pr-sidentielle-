"""Chantier B (préparation) : cartographie chiffrée du compte des sociétés non financières (S11) et financières (S12),
contrôle des identités, ratios de comportement (Eurostat nasa_10_nf_tr, France, M€ courants)."""
import json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
from telechargement import jsonstat_dict
s = pd.Series(jsonstat_dict(json.loads((R / "data" / "raw" / "eurostat_nasa_10_nf_tr_secteurs_FR.json").read_text())))
def v(direct, item, sec, t):
    return float(s.get((direct, item, sec, str(t)), np.nan))
ANS = [2000, 2007, 2012, 2015, 2019, 2022, 2024]
rows = {}
for sec in ("S11", "S12"):
    for t in ANS:
        g = lambda it, d="PAID": v(d, it, sec, t)
        r = {"VA (B1G)": g("B1G", "RECV") if not np.isnan(g("B1G", "RECV")) else g("B1G"), "rémunérations (D1)": g("D1"),
             "impôts production (D29)": g("D29"), "subventions production (D39, reçues)": v("RECV", "D39", sec, t), "EBE (B2G)": g("B2A3G", "RECV") if not np.isnan(g("B2A3G", "RECV")) else g("B2A3G"),
             "intérêts versés (D41)": g("D41"), "intérêts reçus (D41)": v("RECV", "D41", sec, t),
             "dividendes versés (D421)": g("D421"), "dividendes reçus (D421)": v("RECV", "D421", sec, t),
             "bénéfices réinvestis IDE versés (D43)": g("D43"), "bénéfices réinvestis IDE reçus (D43)": v("RECV", "D43", sec, t),
             "IS et impôts courants (D5)": g("D5"), "épargne brute (B8G)": g("B8G", "RECV") if not np.isnan(g("B8G", "RECV")) else g("B8G"),
             "FBCF (P51G)": g("P51G"), "capacité de financement (B9)": g("B9", "RECV") if not np.isnan(g("B9", "RECV")) else g("B9")}
        rows[(sec, t)] = r
df = pd.DataFrame(rows).T / 1000
pd.set_option("display.width", 250)
print("Montants (Md€) :")
print(df.round(1).to_string())
# identité de l'EBE et ratios (S11)
print("\nContrôles et ratios, sociétés non financières (S11) :")
for t in ANS:
    r = rows[("S11", t)]
    ebe_calc = r["VA (B1G)"] - r["rémunérations (D1)"] - r["impôts production (D29)"] + r["subventions production (D39, reçues)"]
    rp = r["EBE (B2G)"] + r["intérêts reçus (D41)"] - r["intérêts versés (D41)"] + r["dividendes reçus (D421)"] - r["dividendes versés (D421)"]
    print(f"{t} : EBE calculé − publié = {(ebe_calc - r['EBE (B2G)']) / 1000:+.1f} Md€ ; taux de marge {100 * r['EBE (B2G)'] / r['VA (B1G)']:.1f} % ; "
          f"dividendes versés nets / EBE {100 * (r['dividendes versés (D421)'] - r['dividendes reçus (D421)']) / r['EBE (B2G)']:.1f} % ; "
          f"IS / EBE {100 * r['IS et impôts courants (D5)'] / r['EBE (B2G)']:.1f} % ; taux d'autofinancement (B8G / FBCF) {100 * r['épargne brute (B8G)'] / r['FBCF (P51G)']:.1f} % ; "
          f"intérêts nets / EBE {100 * (r['intérêts versés (D41)'] - r['intérêts reçus (D41)']) / r['EBE (B2G)']:.1f} %")
df.to_csv(pathlib.Path(__file__).parent / "b1_compte_societes.csv")
