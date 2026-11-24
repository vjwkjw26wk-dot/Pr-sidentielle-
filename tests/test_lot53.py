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
