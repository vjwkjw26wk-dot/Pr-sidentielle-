"""Phase 4.2, chantier A : backtests multi-origines des nouvelles spécifications de prix et salaires."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lab42 import *
import pandas as pd
rows = {}
origines = [(int(a), int(b)) for a, b in (x.split("-") for x in sys.argv[1:] if not x.startswith("--"))] or [(2010, 2019), (2014, 2019), (2021, 2025)]
for B, fin in origines:
    for nom in (SELECTION_C if '--rattrapage' in sys.argv else SELECTION_B if '--brut' in sys.argv else SELECTION if '--selection' in sys.argv else CONFIGS):
        spec = CONFIGS[nom]
        try:
            rows[f"{B}-{fin} {nom}"] = run(B, fin, "v08", spec)
        except Exception as e:  # noqa: BLE001
            import traceback; traceback.print_exc()
cols = ["dette", "pib", "emploi", "chomage", "pc", "pibn", "rmse_pib_g", "rmse_pc_g", "rmse_chom", "rmse_dette"]
print(table(rows, cols))
pd.DataFrame(rows).T.to_csv(pathlib.Path(__file__).parent / "resultats" / f"a6_backtests_{'_'.join(sys.argv[1:]) or 'defaut'}.csv")
