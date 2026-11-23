"""Phase 3.1 — contribution du module zone euro (M11) aux effets des stratégies, configuration centrale : sans le
module, avec le module sans prime de risque, avec la prime centrale (0,03 point de taux par point de dette) et haute (0,05). Sortie : phase31/resultats/diagnostic_europe.json."""
import json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport"), str(R / "phase31")]
from simulateur import executer as X  # noqa: E402
import simulations as SIM  # noqa: E402
import strategies_v08 as SV  # noqa: E402
P = SV.programmes()
V = ("pib", "chomage", "inflation", "dette_pib", "solde_pib", "interets_pib", "taux_apparent", "x", "pc", "pib_potentiel")
out = {}
for k in sys.argv[1:] or ["S3_productivite", "S4_redressement"]:
    out[k] = {}
    for cas, eu, pr in (("sans", False, None), ("avec_prime0", True, 0.0), ("avec", True, 0.03), ("avec_prime5", True, 0.05)):
        hyp = {"europe": eu, "incertitude": 0, "profils": False, "distribution_dynamique": False}
        if pr is not None:
            hyp["prime_risque"] = pr
        sc = {"nom": k, "horizon": 2047, "hypotheses": hyp,
              "mesures": [SIM.CUR[a]["mesure"](v) for a, v in P[k].items()]}
        r = X.executer(X.depuis_curseurs(sc))
        tr = r["trajectoires"]
        out[k][cas] = {v: {t: tr[v]["ecart"][t] for t in (2030, 2035, 2040, 2047)} for v in V if v in tr}
        print(k, cas, {v: round(out[k][cas][v][2047], 2) for v in out[k][cas]}, flush=True)
(R / "phase31" / "resultats" / "diagnostic_europe.json").write_text(json.dumps(out, default=float, indent=1))
