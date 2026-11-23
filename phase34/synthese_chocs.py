"""Synthèse des chocs : effets complets et contributions des boucles (complet − « + boucle » relatif au tout gelé)."""
import json, pathlib, sys
import pandas as pd
D = pathlib.Path(__file__).parent / "resultats"
VARS = ["PIB", "PIB nominal", "emploi (milliers)", "prix conso", "conso", "invest.", "recettes (Md€)", "dépenses (Md€)", "solde (pt PIB)", "dette (pt PIB)"]
for s in sys.argv[1:] or ["v0.8", "v0.9"]:
    f = D / f"chocs_{s}.json"
    if not f.exists():
        continue
    res = json.loads(f.read_text())
    print(f"\n######## {s}")
    for choc, cas in res.items():
        rows = {}
        for c in ("tout gelé", "+ C", "+ prix_salaires", "+ emploi", "+ Z", "complet"):
            for an in ("2028", "2030", "2035"):
                rows[(c, an)] = {k: cas[c][an][k] for k in VARS}
        df = pd.DataFrame(rows).T
        print(f"\n== {choc}  (identité de la dette, écart max : {max(cas[c]['identite_dette_max_M€'] for c in cas):.2e} M€)")
        print(df.loc[[(c, "2030") for c in ("tout gelé", "+ C", "+ prix_salaires", "+ emploi", "+ Z", "complet")] + [("complet", "2028"), ("complet", "2035")]].round(2).to_string())
