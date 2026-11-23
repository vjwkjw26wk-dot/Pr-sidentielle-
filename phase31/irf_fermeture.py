"""Phase 3.1 — réponses impulsionnelles de l'écart de production du modèle à un choc de demande transitoire et à un
choc d'offre permanent, pour une grille de paramètres de fermeture (ρ, θ, part du capital dans l'anticipation).
Sortie : phase31/resultats/irf_<tag>.json (utilisé par estimation_theta.py)."""
import sys, pathlib, copy, pickle, json, itertools
import numpy as np
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
from simulateur import executer as X
mod = X.modele(2022)
ex0 = pickle.loads((R / "outputs/compte_reference_2022_2047.pkl").read_bytes())["exogenes"]
AN = range(2023, 2048)
T0 = 2028
rhos = [float(x) for x in sys.argv[2].split(",")]
thetas = [float(x) for x in sys.argv[3].split(",")]
parts_k = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [1.0]
amortis = [float(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else [0.3]
MU = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
out = {}
for rho, th, pk, am in itertools.product(rhos, thetas, parts_k, amortis):
    def run(z=None, prod=None):
        e = copy.deepcopy(ex0)
        e.comportements = {"PART_K_ANTICIPATION": pk}
        e.mu_import = MU
        e.parametres_alternatifs = {"rho": rho, "amorti": am, "theta": th, "debut": T0, **({"impulsion_Z": z} if z else {})}
        if prod is not None:
            e.productivite = prod
        return mod.simuler(AN, e)
    b = run()
    d = run(z={T0: 0.01, T0 + 1: -0.01})                       # demande : +1 % de la demande pendant un an
    import pandas as pd
    s = run(prod=pd.Series({t: (-0.01 if t == T0 else 0.0) for t in range(2019, 2048)}))   # offre : −1 % de productivité, permanent
    def irf(r, k, log=False):
        if log:
            return [float(100 * (np.log(r[k][t]) - np.log(b[k][t]))) for t in range(T0, 2048)]
        return [float(r[k][t] - b[k][t]) for t in range(T0, 2048)]
    key = f"{rho}|{th}|{pk}|{am}"
    out[key] = {"demande": {"gap": irf(d, "ecart_production"), "pot": irf(d, "pib_potentiel", True), "pib": irf(d, "pib", True), "u": irf(d, "chomage"),
                            "dette": irf(d, "dette_pib")},
                "offre": {"gap": irf(s, "ecart_production"), "pot": irf(s, "pib_potentiel", True), "pib": irf(s, "pib", True), "u": irf(s, "chomage"),
                          "dette": irf(s, "dette_pib")}}
    print(key, "offre", [round(x, 2) for x in out[key]["offre"]["gap"][:8]], "demande", [round(x * 100, 2) for x in out[key]["demande"]["gap"][:8]], flush=True)
    (R / "phase31" / "resultats" / f"irf_{sys.argv[1]}.json").write_text(json.dumps(out))
