"""Tests de la phase 4.2 : non-régression de la v0.9 (interrupteurs par défaut) et propriétés des nouvelles options."""
import json
import pathlib
import sys

import numpy as np
import pytest

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "phase34"), str(R / "src")]


def test_v09_reproduite_backtest_2014():
    """Les options de la phase 4.2 désactivées, la v0.9 reproduit ses valeurs de référence (origine 2014)."""
    from lab import run, V09
    ref = json.loads((R / "phase42" / "resultats" / "reference_v09.json").read_text())["2014-2019 v0.9"]
    res = run(2014, 2019, "v08", V09)
    for k in ("dette", "pib", "emploi", "chomage", "pc"):
        assert res[k] == pytest.approx(ref[k], abs=1e-6), k


def test_v08_reproduite_backtest_2014():
    from lab import run
    ref = json.loads((R / "phase42" / "resultats" / "reference_v09.json").read_text())["2014-2019 v0.8"]
    res = run(2014, 2019, "v08", {})
    for k in ("dette", "pib", "chomage", "pc"):
        assert res[k] == pytest.approx(ref[k], abs=1e-6), k


def test_regle_smic_reproduit_2013_2021():
    import m19_salaires as W
    d = W.donnees()
    err = [abs(W.regle_smic(d, t, d.dlpc[t], d.dlw[t - 1], d.dlpc[t - 1]) - d.dlsmic[t]) for t in range(2013, 2022)]
    assert max(err) < 0.013


def test_prix_ci_base_unitaire():
    """L'indice de prix des consommations intermédiaires vaut 1 dans l'année de base (prix de base unitaires)."""
    import m8_modele as M
    M.configurer_v08()
    M.SPEC.update({"prix_va": "ci_hausse"})
    try:
        mod = M.Modele(2014)
        pci = mod._prix_ci_branches(mod._prix(np.ones(len(mod.P)), np.ones(len(mod.P))), np.ones(len(mod.P)))
        assert all(abs(v - 1) < 1e-9 for v in pci.values())
    finally:
        M.configurer_v08()
