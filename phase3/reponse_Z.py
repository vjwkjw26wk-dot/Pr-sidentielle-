"""Réponse de l'écart de production à une impulsion de demande permanente (+1 % du PIB en 2028), fermeture coupée."""
import sys, pathlib, copy, pickle
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
from simulateur import executer as X
mod = X.modele(2022)
ex0 = pickle.loads((R / "outputs/compte_reference_2022_2047.pkl").read_bytes())["exogenes"]
AN = range(2023, 2048)
import json
var = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
a = copy.deepcopy(ex0)
for k, v in var.items():
    if k in ("mu_import", "kappa_prix"):
        setattr(a, k, v)
    else:
        a.comportements = {**(a.comportements or {}), k: v}
a.parametres_alternatifs = {"rho": 0.0, "debut": 2028}
b = copy.deepcopy(a); b.parametres_alternatifs = {"rho": 0.0, "debut": 2028, "impulsion_Z": {2028: 0.01}}
ra, rb = mod.simuler(AN, a), mod.simuler(AN, b)
for t in range(2027, 2040):
    print(t, round(rb.ecart_production[t] - ra.ecart_production[t], 3), round(100 * (rb.pib[t] / ra.pib[t] - 1), 3),
          round(100 * (rb.pib_potentiel[t] / ra.pib_potentiel[t] - 1), 3), round(rb.chomage[t] - ra.chomage[t], 3), round(100*(rb.pc[t]/ra.pc[t]-1),3))
