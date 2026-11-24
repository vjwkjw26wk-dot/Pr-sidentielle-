"""Phase 4.2, étape 1 : reproductibilité de la v0.9 (backtests de référence) et de la v0.8 (défaut des interrupteurs).
Écrit phase42/resultats/reference_v09.json : valeurs de non-régression pour la suite de la phase."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "phase34"))
from lab import run, V09
out = {}
for B, fin in ((2010, 2019), (2014, 2019), (2021, 2025)):
    for nom, spec in (("v0.8", {}), ("v0.9", V09)):
        out[f"{B}-{fin} {nom}"] = run(B, fin, "v08", spec)
p = pathlib.Path(__file__).parent / "resultats" / "reference_v09.json"
p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
for k, v in out.items():
    print(k, {c: round(v[c], 3) for c in ("dette", "pib", "emploi", "chomage", "pc", "rmse_chom", "rmse_dette")})
