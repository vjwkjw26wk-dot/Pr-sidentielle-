"""Met à jour le cache de la référence calée (outputs/compte_reference_2022_2047.pkl) après une modification de
m8_modele.py qui ne touche pas le calage (lequel est fait avec l'ancienne fermeture, sans lpgf) : recalcule lpgf,
lpot_ref, lk_ref, ly_ref et l'empreinte, sans refaire les 27 minutes de calage. Vérifie que la trajectoire de la
référence est inchangée sous l'ancienne fermeture."""
import sys, pathlib, pickle, hashlib, copy
import numpy as np
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
from simulateur import executer as X
import m8_reference as RF
mod = X.modele(2022)
f = R / "outputs/compte_reference_2022_2047.pkl"
d = pickle.loads(f.read_bytes())
ex = d["exogenes"]
AN = range(2023, 2048)
e0 = copy.deepcopy(ex); e0.lpgf = e0.lpot_ref = e0.lk_ref = e0.ly_ref = None; e0.fermeture_mode = "chomage"
c0 = mod.simuler(AN, e0)
ex.lpgf = c0["lpgf_implicite"].copy(); ex.fermeture_mode = "production"; ex.lpot_ref = ex.lk_ref = ex.ly_ref = None
c1 = mod.simuler(AN, ex)
ex.lpot_ref = np.log(c1["pib_potentiel"]).copy(); ex.lk_ref = np.log(c1["capital_marchand"]).copy(); ex.ly_ref = np.log(c1["pib"]).copy()
c2 = mod.simuler(AN, ex)
print("écart max chômage (production − ancienne fermeture) :", float((c2.chomage - c0.chomage).abs().max()))
print("écart max dette :", float((c2.dette_pib - c0.dette_pib).abs().max()))
emp = hashlib.sha1((pathlib.Path(RF.__file__).read_bytes() + (R / "src" / "m8_modele.py").read_bytes())).hexdigest()[:12]
d["exogenes"], d["empreinte"] = ex, emp
f.write_bytes(pickle.dumps(d))
print("cache mis à jour", emp)
