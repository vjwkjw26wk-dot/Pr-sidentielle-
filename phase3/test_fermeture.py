"""Stabilité de la fermeture sur l'écart de production (v0.7) : reproduction de la référence et chocs d'offre,
pour plusieurs valeurs du terme proportionnel. Lit directement le cache calé (sans recalage)."""
import sys, pathlib, copy, pickle, json
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import pandas as pd
from simulateur import executer as X
sys.path.insert(0, str(R / "rapport")); import verification as V
mod = X.modele(2022)
d = pickle.loads((R / "outputs/compte_reference_2022_2047.pkl").read_bytes())
ex0 = d["exogenes"]; AN = range(2023, 2048)
eo = copy.deepcopy(ex0); eo.lpgf = None; eo.fermeture_mode = "chomage"
old = mod.simuler(AN, eo)
import numpy as np
ex0.lpot_ref = np.log(mod.simuler(AN, ex0)["pib_potentiel"])
TH = float(__import__("os").environ.get("THETA", "1.0"))
res = {}
for am in [float(a) for a in sys.argv[1:]] or [0.3, 0.1, 0.0]:
    e = copy.deepcopy(ex0); e.comportements = {"AMORTI_PRODUCTION": am, "THETA_ANTICIPATION": TH}
    ref = mod.simuler(AN, e)
    out = {"repro_max_ecart_chomage": float((ref.chomage - old.chomage).abs().max()),
           "repro_max_ecart_dette": float((ref.dette_pib - old.dette_pib).abs().max())}
    for nom, f in V.chocs().items():
        if not any(k in nom for k in ("productivit", "mographi", "taux")):
            continue
        ec = copy.deepcopy(e); f(ec); s = mod.simuler(AN, ec)
        out[nom] = {k: {t: round(float(s[k][t] - ref[k][t]) if k in ("chomage", "dette_pib", "solde_pib", "ecart_production") else float(100 * (s[k][t] / ref[k][t] - 1)), 2)
                        for t in (2030, 2032, 2037, 2047)} for k in ("pib", "pib_potentiel", "salaire", "ecart_production", "emploi", "chomage", "pc", "solde_pib", "dette_pib")}
    res[am] = out
    print(am, "repro", round(out["repro_max_ecart_chomage"], 3), round(out["repro_max_ecart_dette"], 2), flush=True)
    for nom in [k for k in out if not k.startswith("repro")]:
        print("  ", nom[:22], {k: list(v.values()) for k, v in out[nom].items()}, flush=True)
    (R / f"phase3/resultats/test_fermeture_{am}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
