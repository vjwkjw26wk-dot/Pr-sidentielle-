"""Tests du lot 5.2 (M24) : politique monétaire et conditions financières."""
import pathlib, sys, warnings
import numpy as np, pandas as pd, pytest
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]


@pytest.fixture(scope="module")
def env():
    import m23_regimes as G
    return G.Environnement.charger("p4", "part_constante")


@pytest.fixture(scope="module")
def r0(env):
    import m23_regimes as G
    return G.simuler(env, G.regime("R0"))["trajectoire"]


def test_estimations_et_statuts():
    import m24_monetaire as M, m11_europe as M11
    p = M.parametres()
    t = M11.Europe().taylor.params
    assert p["bce_lissage"] == pytest.approx(t["i_1"]) and p["bce_inflation"] == pytest.approx(t["pi"])
    assert 0 < p["bund_transmission"] < 1
    for s in ("menages", "entreprises"):
        assert 0 < p[f"{s}_vitesse"] <= 1 and 0.5 < p[f"{s}_transmission_lt"] < 1.2
    assert p["prime_dette"] > 0


def test_regime_bce_sans_choc_identique_au_regime_exogene(env, r0):
    import m23_regimes as G
    for mon in ("bce", {"type": "bce", "anticipations": "rationnelles"}, {"prime": "ecart_reference"}):
        v = G.simuler(env, G.regime("R0", monetaire=mon))["trajectoire"]
        for c in ("pib", "pc", "dette"):
            assert (v[c] - r0[c]).abs().max() <= 1e-10 * r0[c].abs().max(), (mon, c)


def test_choc_permanent_transmission(env, r0):
    import m23_regimes as G, m24_monetaire as M
    p = M.parametres()
    v = G.simuler(env, G.regime("R0", monetaire={"chocs_directeur": {t: 1.0 for t in range(2027, 2048)}}))["trajectoire"]
    assert (v.mon_taux_directeur - r0.mon_taux_directeur).loc[2027:].sub(1.0).abs().max() < 1e-12
    assert (v.mon_oat - r0.mon_oat).loc[2027:].sub(p["bund_transmission"]).abs().max() < 1e-12
    lt_m = (p["menages_court"] + p["menages_long"] * p["bund_transmission"]) / p["menages_vitesse"]
    assert v.mon_ecart_credit_menages[2046] == pytest.approx(lt_m, rel=1e-3)
    di = (v.interets - r0.interets).loc[2027:2040]
    assert (di.diff().dropna() > 0).all() and di[2027] > 0           # transmission progressive à la charge d'intérêts
    assert (v.dette.diff() + v.solde).loc[2027:].abs().max() < 1e-6   # identité de la dette


def test_regle_bce_lissage(env, r0):
    import m23_regimes as G, m24_monetaire as M
    rho = M.parametres()["bce_lissage"]
    v = G.simuler(env, G.regime("R0", monetaire={"type": "bce", "chocs_directeur": {2027: 1.0}}))["trajectoire"]
    d = (v.mon_taux_directeur - r0.mon_taux_directeur)
    assert d[2027] == pytest.approx(1.0)
    assert abs(d[2028] - rho) < 0.05                                  # lissage, réaction à l'inflation et l'activité faible


def test_prime_souveraine(env, r0):
    import m23_regimes as G
    v = G.simuler(env, G.regime("R0", monetaire={"prime": "niveau"}))["trajectoire"]
    assert (v.mon_oat - r0.mon_oat)[2046] > 1.0                       # dette de référence croissante → prime croissante
    def deficit(mod, ex):
        niv = dict(ex.niveaux or {}); s = niv.get("impots_menages_pib", pd.Series(dtype=float)).copy()
        for t in range(2027, 2048):
            s[t] = float(s.get(t, 0.0)) - 1.0
        niv["impots_menages_pib"] = s.sort_index(); ex.niveaux = niv
    a = G.simuler(env, G.regime("R0"), G.Programme("x", deficit))["trajectoire"]
    b = G.simuler(env, G.regime("R0", monetaire={"prime": "ecart_reference"}), G.Programme("x", deficit))["trajectoire"]
    assert (b.mon_ecart_souverain[2040] > 0) and (b.dette_pib[2040] > a.dette_pib[2040])
