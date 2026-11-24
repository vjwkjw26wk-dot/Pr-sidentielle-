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


def _choc(nom):
    sys.path.insert(0, str(R / "phase42" / "a2"))
    from b5_chocs_ancrage import choc
    return choc(nom)


def test_ancrage_choc_salarial_temporaire_T1():
    """Candidate T1 (frontière, sans effet de tension) : après un choc salarial temporaire de 2 % (2011), l'écart
    d'inflation est revenu sous 0,1 point dès la 5e année et le niveau des prix est stabilisé (variation < 0,3 point
    entre la 10e et la 15e année)."""
    import numpy as np
    from lab import run, V09
    spec = {**V09, "prix_va": "frontiere", "tension_prix": "aucune"}
    b = run(2010, 2025, "v08", spec, retour=True)[1]
    v = run(2010, 2025, "v08", spec, exp_mod=_choc("salaires +2 % temporaire"), retour=True)[1]
    lp = 100 * np.log(v.pc / b.pc)
    assert all(abs(lp[t] - lp[t - 1]) < 0.1 for t in range(2015, 2026))
    assert abs(lp[2025] - lp[2020]) < 0.3


def test_pas_d_emballement_choc_de_taux_T1():
    """Un choc de taux permanent de +1 point ne doit pas produire de hausse des prix (désinflation attendue) ni de
    variation annuelle de l'écart de prix supérieure à 1 point (défaut corrigé : tension sur les capacités)."""
    import numpy as np
    from lab import run, V09
    spec = {**V09, "prix_va": "frontiere", "tension_prix": "aucune"}
    b = run(2010, 2025, "v08", spec, retour=True)[1]
    v = run(2010, 2025, "v08", spec, exp_mod=_choc("taux d'intérêt +1 pt permanent"), retour=True)[1]
    lp = 100 * np.log(v.pc / b.pc)
    assert lp[2025] < 0.5
    assert max(abs(lp[t] - lp[t - 1]) for t in range(2012, 2026)) < 1.0
