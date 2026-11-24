"""Lot 5.3 (préparation) : tableau de robustesse et jeux de paramètres applicables sans recalibration."""
import pathlib, sys, warnings
import pandas as pd, pytest
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R)]


def test_robustesse_programme_nul_et_coherence():
    import m23_regimes as G
    env = G.Environnement.charger("p4", "part_constante")
    reg = {"principal": dict(code="R2"), "fermeture lente": dict(code="R2", parametres="fermeture_lente")}
    nul = G.robustesse(env, G.PROGRAMME_NUL, horizons=(5,), regimes=reg)
    assert nul.abs().max().max() < 1e-9
    for jeu in ("fermeture_lente", "fermeture_rapide", "fermeture_chomage"):
        assert G.simuler(env, G.regime("R0", parametres=jeu))["trajectoire"].pib.notna().all()


def test_parametres_structurels_appliques_sans_recalibration():
    import m23_regimes as G, m8_reference as RF
    env = G.Environnement.charger("p4", "part_constante")
    sauv = (RF.caler, RF.compte_reference)
    RF.caler = RF.compte_reference = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("recalibration"))
    try:
        b = G.simuler(env, G.regime("R0", monetaire={"chocs_directeur": {t: 1.0 for t in range(2027, 2048)}}))["trajectoire"]
        for n, v in (("PSI_TAUX", 0.4), ("bund_transmission", 0.6), ("mu_taux", 0.35)):
            x = G.simuler(env, G.regime("R0", monetaire={"chocs_directeur": {t: 1.0 for t in range(2027, 2048)}},
                                        structurels={n: v}))["trajectoire"]
            assert (x.pib - b.pib).abs().max() > 0, n            # le paramètre agit
        with pytest.raises(AssertionError):
            G.regime("R2", structurels={"inconnu": 1.0})
    finally:
        RF.caler, RF.compte_reference = sauv


def test_transfert_des_programmes_exact():
    """M25 : le programme S2 transféré sur l'environnement historique reproduit les exogènes du simulateur."""
    import json
    b = json.loads((R / "phase5" / "resultats" / "lot53_bilan.json").read_text())
    assert b["controle_transfert"] < 1e-12


def test_revalidation_refuse_un_coefficient_modifie():
    import m23_regimes as G, m8_reference as RF
    env = G.Environnement.charger("p4", "part_constante")
    ep0 = RF.empreinte_parametres(env.mod, env.R["exogenes"], env.R["hypotheses"])
    res = env.mod.eq["consommation"].res
    getattr(res, "_results", res).params[0] += 1e-6
    try:
        assert RF.empreinte_parametres(env.mod, env.R["exogenes"], env.R["hypotheses"])["coefficients"] != ep0["coefficients"]
    finally:
        getattr(res, "_results", res).params[0] -= 1e-6
