"""Phase 6 et corpus : contraintes européennes (M26), corpus des programmes (M27), extensions de M25."""
import pathlib
import sys

import pandas as pd
import pytest

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]
import m26_europe_institutions as U  # noqa: E402
import m27_corpus as C  # noqa: E402

REF = pd.DataFrame({"pib_nominal": {2027: 3.18e6}, "is_": {2027: 114_847.0}})


def test_corpus_integrite():
    ids = [m.id for m in C.M]
    assert len(ids) == len(set(ids))
    for m in C.M:
        assert m.sources and all(s in C.SOURCES for s in m.sources), m.id
        assert m.ue is None or m.ue in U.QUALIFICATIONS, m.id
        assert m.quantifiable in ("oui", "partiel", "non")
        assert m.chiffrage in ("candidat", "tiers", "aucun")
        if m.chiffrage == "aucun":
            assert m.montant is None, m.id


def test_paquet_lfi_recoupe_les_totaux_publies():
    """Le document budgétaire LFI : 106,4 Md€ de recettes et 81,7 Md€ de dépenses pour 2027."""
    lfi = [m for m in C.M if m.candidat == "melenchon" and m.montant is not None and m.annee == 2027]
    rec = sum(m.montant for m in lfi if m.montant > 0)
    dep = -sum(m.montant for m in lfi if m.montant < 0)
    assert rec == pytest.approx(106.4, abs=1e-9)
    assert dep == pytest.approx(81.7, abs=1e-9)


def test_conversions_inversent_le_rendement_statique():
    l, _ = C.mesures("melenchon", REF)
    d = {i: (c, v) for c, v, _, i in l}
    assert d["L01"] == ("pfu", pytest.approx(15.0))                 # 9 Md€ / 0,6
    assert d["L04"][1] * 18_000 / 100 == pytest.approx(20_000)      # successions
    assert (d["L02"][1] / 100 * 930_000 - 2_200) == pytest.approx(10_000)
    assert (d["L07"][1] - 25.8) * 114_847 / 25.8 == pytest.approx(3_000)
    assert d["L24"][1] == pytest.approx((1700 / 1477.93 - 1) * 100)


def test_variantes_institutionnelles():
    conf, _ = C.mesures("le_pen", REF, "conforme")
    cont, hors = C.mesures("le_pen", REF, "contentieux")
    c = {i: (v, d) for _, v, d, i in conf}
    k = {i: (v, d) for _, v, d, i in cont}
    assert "P04" in c and "P04" not in k and ("P04", "retirée (incompatibilité européenne)") in hors
    assert k["P10"][0] == pytest.approx(c["P10"][0] * 0.5) and k["P10"][1] == c["P10"][1] + 2
    assert k["P03"] == c["P03"]                                       # part non conforme inconnue : conservée


def test_amendes_pde_et_regime_monetaire():
    t = U.SCENARIOS["tension"]
    am = U.amendes_pde(t)
    assert am == {2028: pytest.approx(0.1), 2029: pytest.approx(0.1)}  # 0,05 % du PIB par semestre, 4 semestres
    assert U.amendes_pde(U.SCENARIOS["conforme"]) == {}
    m = U.regime_monetaire(t)
    import m24_monetaire as M24
    assert m["prime_solde"] == M24.parametres()["prime_solde_avec_crise"]
    assert m["chocs_ecart_souverain"][2028] == 0.5

    class Ex:  # noqa: D401
        calage = {"depenses": pd.Series({2028: 0.2})}
    ex = Ex()
    U.appliquer(t, None, ex)
    assert ex.calage["depenses"][2028] == pytest.approx(0.3) and ex.calage["depenses"][2029] == pytest.approx(0.1)


def test_qualification_politique_commerciale():
    q = U.qualifier({"droits_douane": 10, "pfu": 0, "inconnue": 1})
    assert q[0]["niveau"] == 4 and q[1]["niveau"] is None
    c, _ = U.curseurs_sous_scenario({"droits_douane": 10, "smic": 5}, U.SCENARIOS["conforme"])
    assert c == {"droits_douane": 0, "smic": 5}
