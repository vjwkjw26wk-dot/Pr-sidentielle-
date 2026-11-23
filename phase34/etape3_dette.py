"""Phase 3.4, étape 3 : effet isolé de la dette par cohortes (v0.8 + cohortes ; v0.9 sans/avec cohortes)."""
from lab import *
rows = {}
for B, fin in ((2010, 2019), (2012, 2019), (2014, 2019), (2016, 2019), (2021, 2025)):
    rows[f"{B} v0.8"] = run(B, fin, "v08", {})
    rows[f"{B} v0.8 + cohortes"] = run(B, fin, "v08", {"dette": "cohortes"})
    rows[f"{B} v0.9 sans cohortes"] = run(B, fin, "v08", V09_SANS_DETTE)
    rows[f"{B} v0.9 (avec cohortes)"] = run(B, fin, "v08", V09)
print(table(rows, ["dette", "solde", "pib", "chomage", "pc", "taux_app", "rmse_taux_app", "rmse_dette"]))
pd.DataFrame(rows).T.to_csv(pathlib.Path(__file__).parent / "resultats" / "etape3_dette.csv")
