"""Tests du lot 5.0 (phase 5) : environnement calibré une fois, régimes sans recalibration, programmes, identités.
Nécessitent l'environnement P4 / part_constante en cache (phase5/construire_environnement.py, ≈ 50 min la 1re fois)."""
import copy
import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]


@pytest.fixture(scope="module")
def env():
    import m23_regimes as G
    return G.Environnement.charger("p4", "part_constante")


@pytest.fixture(scope="module")
def sans_recalibration(env):
    """Toute tentative de recalibration pendant un test de régime échoue."""
    import m8_reference as RF
    sauv = (RF.caler, RF.compte_reference)
    def interdit(*a, **k):
        raise RuntimeError("recalibration")
    RF.caler = RF.compte_reference = interdit
    yield
    RF.caler, RF.compte_reference = sauv


def test_regles_parametrables():
    import m23_regimes as G
    r = G.regime("R2", alpha=0.3, beta=0.05, plafond=0.3, dette_cible=60.0, parts={"impots_menages": 0.5, "conso_publique": 0.5})
    assert (r.budgetaire.alpha, r.budgetaire.beta, r.budgetaire.plafond, r.budgetaire.dette_cible) == (0.3, 0.05, 0.3, 60.0)
    with pytest.raises(AssertionError):
        G.regime("R2", parts={"impots_menages": 0.7})


def test_R0_reproduit_l_environnement(env, sans_recalibration):
    import m23_regimes as G
    tr = G.simuler(env, G.regime("R0", monetaire={"taux_court_reference": "derive"}))["trajectoire"]
    for c in ("pib", "pc", "chomage", "dette", "solde", "emploi"):
        assert (tr[c] - env.reference[c]).abs().max() <= 1e-9 * env.reference[c].abs().max(), c


def test_changer_de_regime_sans_recalibrer_et_rapidement(env, sans_recalibration):
    import m23_regimes as G
    for code in ("R1", "R2", "R2_sym"):
        t0 = time.time()
        s = G.simuler(env, G.regime(code))
        assert time.time() - t0 < 120
        assert s["environnement"] == env.empreinte()


def test_identites_et_regle(env, sans_recalibration):
    import m23_regimes as G
    tr = G.simuler(env, G.regime("R2"))["trajectoire"]
    assert (tr.dette.diff() + tr.solde).loc[2026:].abs().max() < 1e-6
    assert max(tr._identite_b8g.abs().max(), tr._identite_b9.abs().max()) < 1e-6
    somme = sum(tr[f"impose_effort_{k}"] for k in G.INSTRUMENTS)
    assert (somme - tr.impose_effort).abs().max() < 1e-12
    de = tr.impose_effort.diff().loc[2027:]
    assert (de >= -1e-12).all() and (de <= 0.5 + 1e-12).all()
    assert tr.impose_effort.loc[:2026].abs().max() == 0.0


def test_programme_nul_et_regle_figee(env, sans_recalibration):
    import m23_regimes as G
    reg = G.regime("R2")
    ref = G.simuler(env, reg)
    e = G.evaluer(env, reg, G.PROGRAMME_NUL, ref=ref)
    assert e["ecart"][["PIB (%)", "dette (pt PIB)", "effort imposé (pt PIB)"]].abs().max().max() < 1e-9


def test_programme_figee_effort_identique(env, sans_recalibration):
    """Règle figée : la trajectoire d'effort de la référence est imposée à la variante (coût du programme non compensé)."""
    import m23_regimes as G
    def baisse(mod, ex):
        niv = dict(ex.niveaux or {}); s = niv.get("impots_menages_pib", pd.Series(dtype=float)).copy()
        for t in range(2028, 2048):
            s[t] = float(s.get(t, 0.0)) - 0.5
        niv["impots_menages_pib"] = s.sort_index(); ex.niveaux = niv
    e = G.evaluer(env, G.regime("R2"), G.Programme("test", baisse))
    assert e["ecart"]["effort imposé (pt PIB)"].abs().max() < 1e-12
    assert e["ecart"]["solde (pt PIB)"][2030] < -0.2          # coût non compensé


def test_conversion_effort_conso_publique(env):
    """1 point de PIB d'effort sur la consommation publique = baisse de son volume de 1 / (part de la consommation
    publique dans le PIB de base) % (défaut corrigé : part rapportée à la VA aux prix de base)."""
    import m23_regimes as G
    reg = G.RegleBudgetaire(type="ajustement", parts={"conso_publique": 1.0})
    ex = copy.deepcopy(env.R["exogenes"])
    app = G.AppliqueurBudgetaire(reg, env.mod, effort_impose={2030: 1.0})
    g0 = ex.conso_publique[2030]
    app(env.mod, ex, 2030, [])
    part = float(env.mod.macro.g_cp[env.mod.B] / env.mod.macro.pib_cp[env.mod.B])
    assert (1 - ex.conso_publique[2030] / g0) * part * 100 == pytest.approx(1.0, rel=1e-12)
