"""Phase 3.4, étape 4 : coût du travail net des subventions sur les rémunérations (CICE 2013-2018, bascule 2019)."""
from lab import *
V09_SANS_CICE = {k: v for k, v in V09.items() if k != "cout_travail"}
rows = {}
for B, fin in ((2010, 2019), (2012, 2019), (2014, 2019), (2016, 2019)):
    rows[f"{B} v0.8"] = run(B, fin, "v08", {})
    rows[f"{B} v0.8 + coût net CICE"] = run(B, fin, "v08", {"cout_travail": "net_subventions"})
    rows[f"{B} v0.9 sans CICE"] = run(B, fin, "v08", V09_SANS_CICE)
    rows[f"{B} v0.9 complète"] = run(B, fin, "v08", V09)
print(table(rows, ["dette", "pib", "emploi", "emploi_m", "chomage", "pc", "pibn", "rmse_pib_g", "rmse_pc_g", "rmse_chom", "rmse_dette"]))
pd.DataFrame(rows).T.to_csv(pathlib.Path(__file__).parent / "resultats" / "etape4_cice.csv")
