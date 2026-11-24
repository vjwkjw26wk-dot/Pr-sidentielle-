"""Banc d'essai de la phase 4.3-4.4 : configurations v0.9, T1, T1 + compte des sociétés (candidate phase 4)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "phase42"))
from lab42 import *  # noqa: F401,F403
from lab42 import CONFIGS, V09, run, table, construire  # noqa: F401
T1 = {**V09, "prix_va": "frontiere", "tension_prix": "aucune"}
P4 = {**T1, "societes": "compte"}
CONFIGS["T1"] = T1
CONFIGS["P4 (T1 + compte des sociétés)"] = P4
CONFIGS["v0.9 + compte des sociétés"] = {**V09, "societes": "compte"}
SELECTION_P4 = ["v0.9", "T1", "v0.9 + compte des sociétés", "P4 (T1 + compte des sociétés)"]

import lab as _lab  # noqa: E402
import m8_modele as _M  # noqa: E402
_construire0 = _lab.construire


def _construire43(B, fin, clos="v08", spec=None, **kw):
    mod, ex, ans = _construire0(B, fin, clos, spec, **kw)
    if _M.SPEC.get("societes") == "compte":
        import m21_societes as S21
        # politique fiscale observée injectée (comme le CICE et les taux) : taux apparent de l'IS de S11
        ex.taux_is_apparent = S21.donnees().taux_is_app
    return mod, ex, ans


_lab.construire = _construire43
