"""Phase 3.4, étape 1 : effet isolé de chaque option v0.9 puis cumul, origines 2010-2021, fermeture v0.8."""
import sys
from lab import *
ETAPES = [("v0.8 (référence)", {}),
          ("A σ = 0,45 (ré-estimé)", {"sigma": 0.45}),
          ("B demande de travail CES en heures", {"demande_travail": "ces_heures"}),
          ("C sans terme de capital", {"cible_k": False}),
          ("D potentiel CES", {"potentiel": "ces_marchand"}),
          ("E non marchand par sous-branche", {"non_marchand": "branches"}),
          ("F salaire public instrument", {"salaire_public": "instrument"}),
          ("A+B+C (bloc travail)", {"sigma": 0.45, "demande_travail": "ces_heures", "cible_k": False}),
          ("A+B+C+D (offre cohérente)", {"sigma": 0.45, "demande_travail": "ces_heures", "cible_k": False, "potentiel": "ces_marchand"}),
          ("v0.9 complète", V09)]
origines = [(int(a), int(b)) for a, b in (x.split("-") for x in sys.argv[1:])] or [(2010, 2019)]
rows = {}
for B, fin in origines:
    for nom, spec in ETAPES:
        try:
            rows[f"{B}-{fin} {nom}"] = run(B, fin, "v08", spec)
        except Exception as e:  # noqa: BLE001
            import traceback; traceback.print_exc(); rows[f"{B}-{fin} {nom}"] = {"dette": np.nan}
cols = ["dette", "pib", "emploi", "emploi_m", "emploi_nm", "chomage", "pc", "pibn", "rmse_chom", "rmse_dette", "okun_moy"]
print(table(rows, [c for c in cols if c in pd.DataFrame(rows).T.columns]))
pd.DataFrame(rows).T.to_csv(pathlib.Path(__file__).parent / "resultats" / f"etape1_{'_'.join(sys.argv[1:]) or '2010-2019'}.csv")
