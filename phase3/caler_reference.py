"""Recalage de la trajectoire de référence (v0.7) pour l'horizon 2047 et 2035 ; écrit les caches outputs/compte_reference_*.pkl."""
import sys, pathlib, time
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]
import m8_reference as RF  # noqa: E402
from simulateur import executer as X  # noqa: E402
mod = X.modele(2022)
for fin in (2047,):
    t0 = time.time()
    d = RF.compte_reference(mod, range(2023, fin + 1))
    tr = d["trajectoire"]
    print(fin, "ok", round(time.time() - t0), "s", flush=True)
    print(tr[["pib", "chomage", "ecart_production", "solde_pib", "dette_pib", "taux_epargne"]].loc[[2025, 2026, 2028, 2030, 2032, 2037, 2047]].round(2), flush=True)
