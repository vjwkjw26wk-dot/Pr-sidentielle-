"""Tests automatisés de la version 0.8 (phase 3.1) : identités comptables, cohérence des modules, stabilité numérique,
absence de comportements paradoxaux, reproductibilité, cohérence des résultats quand les paramètres varient.

Ces tests vérifient des propriétés nécessaires ; ils ne prouvent pas la validité économique du modèle.
Lancement : python3 -m pytest -q tests/test_phase31.py   (environ 25 minutes)
"""
import copy
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport"), str(R / "phase31")]
from simulateur import executer as X  # noqa: E402
import m8_reference as RF  # noqa: E402
import m8_modele as M  # noqa: E402

AN = range(2023, 2048)
_C = {}


@pytest.fixture(scope="module")
def mod():
    return X.modele(2022)


@pytest.fixture(scope="module")
def ref(mod):
    d = RF.compte_reference(mod, AN)
    return d["exogenes"], mod.simuler(AN, d["exogenes"])


def scen(cur, hyp=None):
    import simulations as SIM
    k = (tuple(sorted(cur.items())), tuple(sorted((hyp or {}).items())))
    if k not in _C:
        sc = {"nom": "t", "horizon": 2047, "hypotheses": {"europe": False, "incertitude": 0, "profils": False, **(hyp or {})},
              "mesures": [SIM.CUR[a]["mesure"](v) for a, v in cur.items()]}
        _C[k] = X.executer(X.depuis_curseurs(sc))
    return _C[k]


# ---------------------------------------------------------------- identités comptables et cohérence des flux
def test_dette_et_solde(ref):
    """Identité : dette(t) = dette(t−1) − solde(t) (hors ajustements stock-flux de calage, nuls après 2026)."""
    _, r = ref
    for t in range(2028, 2047):
        assert abs(r.dette[t] - (r.dette[t - 1] - r.solde[t])) / r.dette[t] < 1e-6


def test_ratios(ref):
    """Les ratios au PIB sont cohérents avec les niveaux ; solde = recettes − dépenses."""
    _, r = ref
    assert np.allclose(r.solde_pib, r.solde / r.pib_nominal * 100)
    assert np.allclose(r.dette_pib, r.dette / r.pib_nominal * 100)
    assert np.allclose(r.solde, r.recettes - r.depenses, rtol=1e-9, atol=1e-3)


def test_reference_identique_sous_les_deux_fermetures(mod, ref):
    ex, a = ref
    e2 = copy.deepcopy(ex)
    e2.lpgf = e2.lpot_ref = e2.lk_ref = e2.ly_ref = None
    e2.fermeture_mode = "chomage"
    b = mod.simuler(AN, e2)
    assert float((a.chomage - b.chomage).abs().max()) < 0.05
    assert float((a.dette_pib - b.dette_pib).abs().max()) < 0.5


# ---------------------------------------------------------------- stabilité numérique et reproductibilité
def test_reproductibilite(mod, ref):
    """Deux simulations identiques donnent des résultats identiques (aucun aléa caché)."""
    ex, a = ref
    b = mod.simuler(AN, copy.deepcopy(ex))
    pd.testing.assert_frame_equal(a, b)


def test_amortissement_du_point_fixe_independant_de_la_fermeture(mod, ref):
    """Le défaut de la v0.7 (le terme proportionnel de la fermeture écrasait l'amortissement du point fixe) ne doit
    pas revenir : changer le terme proportionnel à partir de 2028 ne modifie pas les années antérieures."""
    ex, a = ref
    e = copy.deepcopy(ex)
    e.parametres_alternatifs = {"amorti": 0.0, "debut": 2028}
    b = mod.simuler(AN, e)
    assert float((a.pib.loc[:2027] - b.pib.loc[:2027]).abs().max()) < 1e-6


def test_choc_ponctuel_sans_oscillation(mod, ref):
    """Après un choc d'offre ponctuel (productivité −1 % en 2028), l'écart de production décroît sans changer de signe
    de plus de 10 % de l'écart initial (pas d'oscillation de période deux ans)."""
    ex, a = ref
    e = copy.deepcopy(ex)
    e.productivite = pd.Series({t: (-0.01 if t == 2028 else 0.0) for t in range(2019, 2048)})
    b = mod.simuler(AN, e)
    g = (b.ecart_production - a.ecart_production).loc[2028:2040].values
    assert g[0] > 0.5
    assert g.min() > -0.1 * g[0]
    assert g[8] < 0.5 * g[0]


# ---------------------------------------------------------------- absence de comportements paradoxaux
def test_chocs_d_offre(mod, ref):
    """Un choc de productivité ou de démographie défavorable réduit le PIB et le PIB potentiel ; l'écart de production reste faible (pas de comportement paradoxal)."""
    import verification as V
    ex, a = ref
    for nom, f in V.chocs().items():
        if "productivit" not in nom and "mographi" not in nom:
            continue
        e = copy.deepcopy(ex)
        f(e)
        b = mod.simuler(AN, e)
        assert b.pib[2037] < a.pib[2037]
        assert b.pib_potentiel[2037] < a.pib_potentiel[2037]
        assert abs(b.ecart_production[2037] - a.ecart_production[2037]) < 1.0


def test_taux(mod, ref):
    """Une hausse des taux réduit l'investissement et augmente la dette."""
    import verification as V
    ex, a = ref
    f = [g for n, g in V.chocs().items() if "taux" in n][0]
    e = copy.deepcopy(ex)
    f(e)
    b = mod.simuler(AN, e)
    assert b.fbcf[2032] < a.fbcf[2032] and b.dette_pib[2032] > a.dette_pib[2032]


# ---------------------------------------------------------------- incidence et distribution dynamique
def test_incidence_is_sur_les_salaires():
    """Une hausse d'IS réduit le coût salarial de long terme quand l'incidence salariale est positive, pas sinon."""
    c = scen({"taux_is": 30.5})["trajectoires"]["salaire"]["ecart"][2040]
    b = scen({"taux_is": 30.5}, {"comportements_v07": "basse"})["trajectoires"]["salaire"]["ecart"][2040]
    assert c < b


def test_distribution_dynamique_coherente():
    """Le contrôle de cohérence de M16 : la somme des canaux micro reproduit la variation macroéconomique du revenu
    disponible à 1,5 point près ; le canal direct est nul avant la mise en œuvre (2027)."""
    r = scen({"rsa": 25})
    d = r["distribution_dynamique"]
    for t, v in d.items():
        if int(t) >= 2030:
            assert abs(v["global"]["coherence"]["residuel_pct"]) < 1.5
    assert abs(d[2027]["global"]["canaux_pct"]["direct"]) < 1e-9 if 2027 in d else True


def test_distribution_dynamique_sens():
    """Une hausse du RSA profite d'abord au premier décile ; une hausse de TVA réduit le revenu réel moyen."""
    r = scen({"rsa": 25})["distribution_dynamique"][2030]
    assert r["decile"]["1"]["pct"] > r["decile"]["10"]["pct"]
    t = scen({"tva": 1})["distribution_dynamique"][2030]
    assert t["global"]["pct_moyen"] < 0


# ---------------------------------------------------------------- cohérence quand les paramètres varient
def test_monotonie_offre_de_travail():
    """Les effets de la prime d'activité sur la population active sont ordonnés selon les élasticités basse, centrale, haute."""
    import m15_offre_travail as M15
    v = [M15.effets({"prime_activite": 0.25}, n)["population_active_milliers"] for n in ("basse", "centrale", "haute")]
    assert v[0] < v[1] < v[2]


def test_monotonie_anticipation(mod, ref):
    """Plus l'anticipation est forte, plus la production rejoint vite le potentiel après un choc d'offre."""
    ex, a = ref
    gaps = []
    for th in (0.5, 0.75, 1.0):
        e = copy.deepcopy(ex)
        e.productivite = pd.Series({t: (-0.01 if t == 2028 else 0.0) for t in range(2019, 2048)})
        e.parametres_alternatifs = {"theta": th, "debut": 2028}
        b = mod.simuler(AN, e)
        gaps.append(float((b.ecart_production - a.ecart_production).loc[2029:2033].sum()))
    assert gaps[0] > gaps[1] > gaps[2]


def test_distribution_reforme_age_et_assurance_chomage():
    """Correction phase 3.1 : le relèvement de l'âge légal ne fait pas du premier décile un gagnant (les emplois
    maintenus vont aux ménages proches de l'âge légal, la pension non versée est une perte) ; la baisse des
    allocations chômage fait perdre d'abord les premiers déciles ; la cohérence micro-macro est assurée."""
    a = scen({"age_legal": 65})["distribution_dynamique"][2035]
    assert a["decile"]["1"]["pct"] < 0.5
    assert abs(a["global"]["coherence"]["residuel_pct"]) < 0.5
    c = scen({"assurance_chomage": -25})["distribution_dynamique"][2035]
    assert c["decile"]["1"]["pct"] < c["decile"]["10"]["pct"] < 0
    assert abs(c["global"]["coherence"]["residuel_pct"]) < 0.5
