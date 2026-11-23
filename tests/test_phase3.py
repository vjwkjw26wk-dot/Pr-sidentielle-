"""Tests de cohérence comportementale du modèle v0.7 (phase 3).

Chaque test vérifie un signe ou un ordre de grandeur attendu par la théorie ou la littérature empirique, sur des
simulations exécutées (aucune valeur codée en dur issue d'un résultat). Durée : environ 20 minutes (simulations).
Lancement : python3 -m pytest -q tests/test_phase3.py
"""
import copy
import pathlib
import sys

import numpy as np
import pytest

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport")]
from simulateur import executer as X  # noqa: E402
from simulateur import catalogue as K  # noqa: E402
import m8_reference as RF  # noqa: E402
import m15_offre_travail as M15  # noqa: E402

AN = range(2023, 2048)
_CACHE = {}


@pytest.fixture(scope="module")
def mod():
    return X.modele(2022)


@pytest.fixture(scope="module")
def refx(mod):
    return RF.compte_reference(mod, AN)


def scenario(curseurs, horizon=2047, hyp=None):
    """Écarts au compte de référence (scénario − référence) pour un jeu de curseurs ; mis en cache."""
    cle = (tuple(sorted(curseurs.items())), horizon, tuple(sorted((hyp or {}).items())))
    if cle not in _CACHE:
        import simulations as SIM
        _CACHE[cle] = SIM.simuler("test", curseurs, horizon=horizon, hyp=hyp)["traj"]
    return _CACHE[cle]


def ec(tr, k, t):
    return tr[k]["ecart"][t]


def pct(tr, k, t):
    return 100 * (tr[k]["scenario"][t] / tr[k]["reference"][t] - 1)


# ---------------------------------------------------------------------------------------------------------------
# 1. Fermeture macroéconomique
# ---------------------------------------------------------------------------------------------------------------
def test_reference_identique_sous_les_deux_fermetures(mod, refx):
    """La nouvelle fermeture ne modifie pas la référence calée (écart de production nul par construction)."""
    ex = refx["exogenes"]
    a = mod.simuler(AN, ex)
    e2 = copy.deepcopy(ex)
    e2.lpgf, e2.lpot_ref, e2.fermeture_mode = None, None, "chomage"
    b = mod.simuler(AN, e2)
    assert float((a.chomage - b.chomage).abs().max()) < 0.15
    assert float((a.dette_pib - b.dette_pib).abs().max()) < 1.5


def _choc(mod, refx, f):
    ex = copy.deepcopy(refx["exogenes"])
    ref = mod.simuler(AN, ex)
    f(ex)
    return ref, mod.simuler(AN, ex)


def test_choc_de_productivite_defavorable(mod, refx):
    """Productivité −0,3 pt/an : le PIB baisse vers le potentiel, l'écart de production se referme, la dette augmente
    à long terme (le paradoxe de la v0.6 — baisse du chômage et de la dette — ne doit plus apparaître)."""
    import verification as V
    f = [g for n, g in V.chocs().items() if "productivit" in n][0]
    ref, s = _choc(mod, refx, f)
    pib = 100 * (s.pib / ref.pib - 1)
    pot = 100 * (s.pib_potentiel / ref.pib_potentiel - 1)
    assert pib[2037] < -2.0 and pot[2037] < -2.0
    assert abs(s.ecart_production[2037] - ref.ecart_production[2037]) < 1.0
    assert s.dette_pib[2047] - ref.dette_pib[2047] > 0


def test_choc_demographique(mod, refx):
    """Population active −0,2 %/an : PIB plus faible, potentiel plus faible, écart de production proche de zéro."""
    import verification as V
    f = [g for n, g in V.chocs().items() if "mographi" in n][0]
    ref, s = _choc(mod, refx, f)
    assert 100 * (s.pib[2037] / ref.pib[2037] - 1) < -0.8
    assert abs(s.ecart_production[2037] - ref.ecart_production[2037]) < 1.0


def test_hausse_des_taux(mod, refx):
    """Taux longs +1,5 point : investissement et PIB plus faibles, dette plus élevée."""
    import verification as V
    f = [g for n, g in V.chocs().items() if "taux" in n][0]
    ref, s = _choc(mod, refx, f)
    assert s.fbcf[2032] < ref.fbcf[2032]
    assert s.pib[2032] < ref.pib[2032]
    assert s.dette_pib[2032] > ref.dette_pib[2032]


def test_demande_capacites(mod, refx):
    """Un supplément de demande permanent augmente d'abord la production ; avec le temps, les prix montent et l'effet
    sur le PIB s'érode (contrainte de capacité, Phillips)."""
    ex = copy.deepcopy(refx["exogenes"])
    ex.parametres_alternatifs = {"rho": 0.0, "debut": 2028}
    a = mod.simuler(AN, ex)
    ex.parametres_alternatifs = {"rho": 0.0, "debut": 2028, "impulsion_Z": {2028: 0.01}}
    b = mod.simuler(AN, ex)
    assert b.pib[2028] > a.pib[2028]
    assert b.pc[2035] / a.pc[2035] > b.pc[2029] / a.pc[2029] > 0.999
    assert (b.ecart_production[2039] - a.ecart_production[2039]) < (b.ecart_production[2028] - a.ecart_production[2028])


# ---------------------------------------------------------------------------------------------------------------
# 2. Prix et fiscalité
# ---------------------------------------------------------------------------------------------------------------
def test_tva_asymetrique():
    """Les baisses de TVA sont moins répercutées que les hausses (Benzarti et al. 2020)."""
    R7 = X.REPERCUSSION_TVA_V07
    assert R7[("normal", "hausse")] > R7[("normal", "baisse")]
    assert R7[("reduit", "hausse")] > R7[("reduit", "baisse")]


def test_tva_simulee_asymetrique():
    hausse, baisse = scenario({"tva": 1}, horizon=2035), scenario({"tva": -1}, horizon=2035)
    assert pct(hausse, "pc", 2030) > 0 > pct(baisse, "pc", 2030)
    assert abs(pct(hausse, "pc", 2030)) > abs(pct(baisse, "pc", 2030))


def test_is_baisse_pas_d_investissement_automatique():
    """Baisser l'IS n'augmente l'investissement que par le canal de la trésorerie : effet faible, et nul avec le
    comportement « basse » (CICE, réforme des dividendes de 2013)."""
    c = scenario({"taux_is": 20}, horizon=2035)
    b = scenario({"taux_is": 20}, horizon=2035, hyp={"comportements_v07": "basse"})
    assert pct(c, "fbcf", 2032) < 1.0
    assert pct(b, "fbcf", 2032) <= pct(c, "fbcf", 2032) + 0.05


def test_is_transfert_de_benefices():
    """Le rendement d'une hausse d'IS est diminué par le transfert de bénéfices (semi-élasticité > 0)."""
    c = scenario({"taux_is": 28}, horizon=2035)
    b = scenario({"taux_is": 28}, horizon=2035, hyp={"comportements_v07": "basse"})
    assert ec(c, "solde_pib", 2030) < ec(b, "solde_pib", 2030)


# ---------------------------------------------------------------------------------------------------------------
# 3. Offre de travail
# ---------------------------------------------------------------------------------------------------------------
def test_offre_travail_rsa_prime_activite():
    """Hausse du RSA : population active plus faible ; hausse de la prime d'activité : plus forte (M15)."""
    rsa = M15.effets({"rsa": 0.25}, "centrale")
    ppa = M15.effets({"prime_activite": 0.25}, "centrale")
    assert rsa["population_active_milliers"] < 0 < ppa["population_active_milliers"]


def test_offre_travail_heterogene():
    """Les réactions diffèrent selon la situation familiale : le RSA ne touche pas la participation des personnes en
    couple dont le conjoint travaille ; la prime d'activité augmente la participation mais réduit un peu les heures
    des seconds apporteurs (effet revenu à la marge intensive)."""
    rsa = M15.effets({"rsa": 0.25}, "centrale")["detail"]
    ppa = M15.effets({"prime_activite": 0.25}, "centrale")["detail"]
    assert rsa["rsa|seul"]["participation_milliers"] < 0
    assert rsa["rsa|couple_enfants_conjoint_emploi"]["participation_milliers"] == 0
    assert ppa["prime_activite|couple_enfants_conjoint_emploi"]["participation_milliers"] > 0
    assert ppa["prime_activite|couple_enfants_conjoint_emploi"]["heures_equivalent_milliers"] <= 0


def test_niveaux_de_comportement_ordonnes():
    """Sensibilité : l'élasticité de participation basse < centrale < haute."""
    v = [M15.effets({"prime_activite": 0.25}, n)["population_active_milliers"] for n in ("basse", "centrale", "haute")]
    assert v[0] < v[1] < v[2]
