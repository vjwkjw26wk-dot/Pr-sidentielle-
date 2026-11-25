"""Finalisation (novembre 2026) : retraites (durée d'assurance, groupes de départ anticipé), lecture par objectifs
budgétaires, correspondances du corpus."""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]
import m9_retraites as M9  # noqa: E402


def test_duree_requise_legislation():
    """LFSS pour 2026 : 170 trimestres pour 1963 et 1964, 172 à partir de 1966 ; loi de 2014 : 172 pour 1973."""
    assert M9.duree_requise(1963) == 170 and M9.duree_requise(1964) == 170
    assert M9.duree_requise(1965) == 171 and M9.duree_requise(1966) == 172 and M9.duree_requise(1990) == 172
    assert M9.duree_requise(1973, "2014") == 172 and M9.duree_requise(1964, "2014") == 169
    # réforme : générations atteignant l'âge légal avant 2028 non concernées
    assert M9.duree_requise(1964, "180@2028:progressif") == 170
    assert M9.duree_requise(1990, "180@2028:progressif") == 180 and M9.duree_requise(1990, "168@2028") == 168


@pytest.fixture(scope="module")
def act():
    return M9.ActiviteSeniors()


def test_regle_simple_inchangee_et_options_neutres(act):
    """Sans option, le calcul est celui de la version 0.1 ; un groupe de part nulle ne change rien."""
    for t in (2030, 2040):
        a = act.population_active(t, "65@2028:progressif")
        b = act.population_active(t, "65@2028:progressif|G=60:0")
        assert b == pytest.approx(a, rel=1e-12)


def test_sens_des_effets(act):
    base = act.population_active(2035, "62@2028:immediat")
    assert act.population_active(2035, "62@2028:immediat|D=168@2028") < base          # durée plus courte
    assert act.population_active(2035, "62@2028:immediat|G=60:0.17") < base           # carrières longues à 60 ans
    h = act.population_active(2035, "65@2028:progressif")
    assert act.population_active(2035, "65@2028:progressif|D=180@2028:progressif") > h
    assert act.population_active(2035, "65@2028:progressif|G=ref:0.333") < h          # un tiers aux conditions actuelles


def test_effets_generationnels(act):
    e = M9.effets_generationnels("65@2028:progressif|D=180@2028:progressif", act, generations=(1960, 1980))
    old, young = e[e.generation == 1960], e[e.generation == 1980]
    assert (old.ecart_pivot_ans.abs() < 1e-12).all()
    assert (young.ecart_pivot_ans > 0).all() and (young.facteur_pension < 1).all()
    # report par année de durée : 9 mois (hommes), 5 mois (femmes) — Bozio (2011)
    m = young[young.sexe == "M"].iloc[0]
    assert m.pivot_regle - m.pivot_actuel == pytest.approx(act.theta["M"][4] * 1.0 + 0.75 * 2.0, abs=1e-9)


def test_objectif_budgetaire_interpolation():
    import m23_regimes as G
    o = G.ObjectifBudgetaire(cibles={2027: -6.0, 2032: -2.5}, parts={"prestations": 1.0})
    assert o.cible(2026) == -6.0 and o.cible(2040) == -2.5
    assert o.cible(2030) == pytest.approx(-6.0 + 3 / 5 * 3.5)
    with pytest.raises(AssertionError):
        G.ObjectifBudgetaire(parts={"prestations": 0.5})


def test_corpus_retraites_et_objectifs():
    import m27_corpus as C
    ref = pd.DataFrame({"pib_nominal": {2027: 3.18e6}, "is_": {2027: 114_847.0}})
    for cand, age in (("melenchon", 62), ("le_pen", 62), ("philippe", 65)):
        l, _ = C.mesures(cand, ref)
        r = [v for c, v, _, _ in l if c == "retraites"]
        assert len(r) == 1 and r[0]["age"] == age
        assert set(C.OBJECTIFS[cand]) >= {"cibles", "parts", "texte", "sources"}
        assert all(s in C.SOURCES for s in C.OBJECTIFS[cand]["sources"])
    import simulateur.executer as X
    assert X.regle_age({"age": 62, "debut": 2028, "mode": "immediat", "duree": 168, "groupe": 60, "groupe_part": 0.17}) \
        == "62@2028:immediat|D=168@2028:immediat|G=60:0.17"


def test_variante_environnement_transmise_au_regime_monetaire():
    """Correction du 24 novembre 2026 : une variante de taux longs (OAT 3,82 %) n'est plus écrasée par l'appliqueur
    monétaire à partir de 2027."""
    import m23_regimes as G
    env = G.Environnement.charger("p4", "part_constante")
    a = G.simuler(env, G.regime("R2"))["trajectoire"]
    b = G.simuler(env, G.regime("R2"), variante_env=G.variante_oat())["trajectoire"]
    assert abs(float(b.interets[2035] - a.interets[2035])) > 0.01 * float(a.interets[2035])
    assert float(b.dette_pib[2040]) < float(a.dette_pib[2040])


def test_investissement_hors_apu_sans_double_compte():
    """Investissement hors APU (L33) : effet de demande ex ante égal au montant, aucune dépense publique directe,
    pas de hausse directe de la dette publique ; la FBCF des branches marchandes n'est pas augmentée en plus du montant
    (seul l'accélérateur induit s'ajoute)."""
    import m23_regimes as G, m25_programmes as P
    env_h = G.Environnement.charger("p4", "historique")
    env = G.Environnement.charger("p4", "part_constante")
    tr = P.traduire([("investissement_hors_apu", 10.0, 2028)], env_h, "test_hors_apu", microsimulation="calcul")
    e = G.evaluer(env, G.regime("R2"), P.programme(tr))
    a, b = e["variante"]["trajectoire"], e["reference"]["trajectoire"]
    assert float(a.fbcf[2027] - b.fbcf[2027]) == pytest.approx(0.0, abs=1e-6)          # rien avant le début
    d_fbcf_vol = float(a.fbcf[2028] - b.fbcf[2028]) / 1e3                                  # Md€ en volume (prix 2022)
    d_dep = float(a.depenses[2028] - b.depenses[2028]) / 1e3                               # Md€ courants
    assert d_dep < 1.0                                                                     # pas de coût public direct
    assert float(a.solde_pib[2028] - b.solde_pib[2028]) > 0                               # recettes induites seulement
    assert 7.0 < d_fbcf_vol < 13.0      # 10 Md€ courants déflatés (≈ 8,5 en volume) + accélérateur induit
    assert float(a.dette_pib[2030] - b.dette_pib[2030]) < 0
