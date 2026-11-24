"""Tests de la phase 4.3-4.4 : compte des sociétés (M21), intégration dans M8, validation prédictive (M22),
non-régression de la v0.9 (interrupteur par défaut) et stabilité de la configuration candidate P4."""
import json
import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "phase43"), str(R / "phase34"), str(R / "src")]


# ---------------------------------------------------------------------------------------------------------- unitaires
def test_identites_compte_societes_donnees():
    """Les soldes du compte de S11 se recomposent exactement à partir des opérations (B8G et B9, 1995-2025)."""
    import m21_societes as S
    d = S.donnees()
    b8g = d.ebe - d.int_nets - d.div_nets - d.d43_nets + d.d44_45_nets - d.is_ + d.autres_courants
    assert (d.b8g - b8g).abs().max() < 1e-6
    assert (d.b9 - (d.b8g - d.fbcf - d.autres_capital)).abs().max() < 1e-6
    # EBE = VA − D1 − D29 + D39 (contrôle déjà fait en préparation, phase42/b) : ordre de grandeur du taux de marge
    assert 0.28 < float((d.ebe / d.va).loc[2000:2019].mean()) < 0.34


def test_compte_societes_isole_continuite_et_identites():
    """Moteurs à leur valeur de base et taux inchangés : le compte reproduit l'année de base (intérêts, IS, épargne) à
    la règle de distribution près, et ses identités sont exactes."""
    import m21_societes as S
    c = S.CompteSocietes(2019)
    c.initialiser()
    d = c.d
    o = c.compte(2020, 1.0, 1.0, 1.0, 1.0, float(d.taux_long[2019]), 1.0, 1.0, taux_court=float(d.taux_court[2019]))
    assert abs(o["_identite_b8g"]) < 1e-9 and abs(o["_identite_b9"]) < 1e-9
    assert o["is_s11"] == pytest.approx(float(d.is_[2019]), rel=0.05)
    assert o["dividendes_distribues"] == pytest.approx(c.rho_B * float(d.profit[2019]), rel=1e-9)
    assert o["interets_s11"] == pytest.approx(float(d.int_nets[2019]), rel=0.25)


def test_hausse_des_taux_augmente_les_interets_et_reduit_les_dividendes():
    import m21_societes as S
    out = {}
    for dr in (0.0, 1.0):
        c = S.CompteSocietes(2019); c.initialiser(); d = c.d
        for t in range(2020, 2026):
            o = c.compte(t, 1.0, 1.0, 1.0, 1.0, float(d.taux_long[2019]) + dr, 1.0, 1.0, taux_court=float(d.taux_court[2019]) + dr)
        out[dr] = o
    # +1 pt sur environ 2 300 Md€ de dette : intérêts versés en hausse de plus de 15 Md€ après six ans ; les intérêts
    # reçus suivent (rapport de base 0,77), d'où une hausse nette plus faible mais positive
    assert out[1.0]["interets_verses_s11"] > out[0.0]["interets_verses_s11"] + 15e3
    assert out[1.0]["interets_s11"] > out[0.0]["interets_s11"]
    assert out[1.0]["dividendes_distribues"] < out[0.0]["dividendes_distribues"]
    assert out[1.0]["dette_s11"] > out[0.0]["dette_s11"]


def test_millesime_fmi_disponible_et_ex_ante_sans_information_future():
    """La demande extérieure ex ante vient du millésime d'octobre de l'origine et diffère de l'observée."""
    import m22_validation as V
    g = V.demande_ex_ante(2014)
    assert np.isfinite(g.loc[2015:2019]).all()
    p = V.previsions_fmi(2014)
    assert np.isfinite(p.loc[2015:2019, ["pib_g", "inflation", "chomage"]].values).all()


# ------------------------------------------------------------------------------------------------ non-régression
def test_v09_reproduite_apres_phase43():
    """SPEC['societes'] par défaut : la v0.9 reproduit ses valeurs de référence (origine 2014)."""
    from lab import run, V09
    ref = json.loads((R / "phase42" / "resultats" / "reference_v09.json").read_text())["2014-2019 v0.9"]
    res = run(2014, 2019, "v08", V09)
    for k in ("dette", "pib", "emploi", "chomage", "pc"):
        assert res[k] == pytest.approx(ref[k], abs=1e-6), k


def test_configurations_sans_fuite_d_etat():
    """Défaut corrigé en phase 4.3 : configurer_v08 doit rétablir σ (un essai v0.9 ne doit pas modifier un essai v0.8
    lancé ensuite) et configurer_phase4 doit conserver σ = 0,45."""
    import m7_equations as E
    import m8_modele as M
    M.configurer_phase4()
    assert E.SIGMA_TRAVAIL == 0.45 and M.SPEC["societes"] == "compte"
    M.configurer_v08()
    assert E.SIGMA_TRAVAIL == M._SIGMA_V08 and M.SPEC["societes"] == "v09"


def test_v08_reproduite_apres_un_essai_v09():
    from lab import run, V09
    ref = json.loads((R / "phase42" / "resultats" / "reference_v09.json").read_text())["2014-2019 v0.8"]
    run(2014, 2019, "v08", V09)
    res = run(2014, 2019, "v08", {})
    assert res["dette"] == pytest.approx(ref["dette"], abs=1e-6)


# --------------------------------------------------------------------------------------------------- intégration
@pytest.fixture(scope="module")
def p4_2014():
    from lab43 import run, CONFIGS
    return run(2014, 2019, spec=CONFIGS["P4 (T1 + compte des sociétés)"], retour=True)


def test_p4_identites_et_lien_menages(p4_2014):
    res, r, mod, o = p4_2014
    assert r[["_identite_b8g", "_identite_b9"]].abs().max().max() < 1e-6
    # revenus du patrimoine des ménages = indexation (hors dividendes) + part des ménages des dividendes distribués
    soc = mod.soc
    for t in r.index:
        attendu = float(mod.men.d4[2014]) * mod.A_courant["pib_nom_idx"][t] + soc.part_men * soc.ecart_div(t, mod.A_courant["pib_nom_idx"][t])
        assert r.revenus_patrimoine_menages[t] == pytest.approx(attendu, rel=1e-9)


def test_p4_backtest_proche_de_t1(p4_2014):
    """Le compte des sociétés ne dégrade pas les agrégats macro de la rétrosimulation 2014-2019 (écart < 0,3 pt)."""
    from lab43 import run, CONFIGS
    res = p4_2014[0]
    t1 = run(2014, 2019, spec=CONFIGS["T1"])
    for k in ("pib", "pc", "emploi", "chomage"):
        assert abs(res[k] - t1[k]) < 0.3, k
    assert abs(res["dette"] - t1["dette"]) < 1.0


def test_p4_choc_de_taux_stable_sur_15_ans():
    """Choc de taux permanent de +1 point (2011) sur la rétrosimulation 2010-2025 : pas d'emballement des prix, charge
    d'intérêts des sociétés en hausse, dividendes en baisse."""
    from lab43 import run, CONFIGS
    sys.path.insert(0, str(R / "phase42" / "a2"))
    from b5_chocs_ancrage import choc
    spec = CONFIGS["P4 (T1 + compte des sociétés)"]
    b = run(2010, 2025, "v08", spec, retour=True)[1]
    v = run(2010, 2025, "v08", spec, exp_mod=choc("taux d'intérêt +1 pt permanent"), retour=True)[1]
    lp = 100 * np.log(v.pc / b.pc)
    assert lp[2025] < 0.5 and max(abs(lp[t] - lp[t - 1]) for t in range(2012, 2026)) < 1.0
    assert (v.interets_s11 - b.interets_s11).loc[2013:2019].min() > 0
    assert (v.dividendes_distribues - b.dividendes_distribues).loc[2014:2019].max() < 0
