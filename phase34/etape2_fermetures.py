"""Phase 3.4, étape 2 : fermetures v0.6 (écart de chômage) et v0.8 (écart de production) sous v0.8 et v0.9."""
from lab import *
rows = {}
for B, fin in ((2010, 2019), (2012, 2019), (2014, 2019)):
    for nom, spec in (("v0.8", {}), ("v0.9", V09)):
        for clos in ("v08", "v06", "demande"):
            rows[f"{B} {nom} fermeture {clos}"] = run(B, fin, clos, spec)
cols = ["dette", "pib", "emploi", "chomage", "pc", "pibn", "rmse_pib_g", "rmse_chom", "rmse_dette", "okun_moy"]
print(table(rows, cols))
pd.DataFrame(rows).T.to_csv(pathlib.Path(__file__).parent / "resultats" / "etape2_fermetures.csv")
