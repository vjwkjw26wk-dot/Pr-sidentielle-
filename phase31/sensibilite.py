"""Phase 3.1 — analyse de sensibilité un à un (valeur basse puis haute de chaque paramètre, les autres à leur valeur
centrale) des stratégies S1 à S5 : effets sur le PIB, le chômage, le solde et la dette en 2030, 2035 et 2047.
Modèle macroéconomique seul (sans zone euro ni distribution, pour limiter le temps de calcul) ; la référence est
recalculée avec les mêmes paramètres que le scénario.
Sortie : phase31/resultats/sensibilite_<stratégie>.json ; classement des paramètres par effet sur la dette en 2047."""
import json, pathlib, sys, time
R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "rapport"), str(R / "phase31")]
from simulateur import executer as X  # noqa: E402
import simulations as SIM  # noqa: E402
import strategies_v08 as SV  # noqa: E402
OUT = R / "phase31" / "resultats"
PARAMS = {  # nom : (hypothèses basse, hypothèses haute, libellé)
    "theta": ({"surcharges": {"THETA_ANTICIPATION": 0.5}}, {"surcharges": {"THETA_ANTICIPATION": 1.0}}, "Anticipation du potentiel θ (0,5 / 1,0)"),
    "rho": ({"fermeture_offre": 0.1}, {"fermeture_offre": 0.3}, "Rappel vers le potentiel ρ (0,1 / 0,3)"),
    "part_k": ({"surcharges": {"PART_K_ANTICIPATION": 0.0}}, {"surcharges": {"PART_K_ANTICIPATION": 1.0}}, "Part du capital dans l'anticipation (0 / 1)"),
    "kappa": ({"surcharges": {"KAPPA_PRIX": 0.05}}, {"surcharges": {"KAPPA_PRIX": 0.18}}, "Phillips prix κ (0,05 / 0,18)"),
    "precaution": ({"surcharges": {"PSI_CHOMAGE": 0.1}}, {"surcharges": {"PSI_CHOMAGE": 0.6}}, "Épargne de précaution (0,1 / 0,6)"),
    "taux_reel": ({"surcharges": {"PSI_TAUX": 0.0}}, {"surcharges": {"PSI_TAUX": 0.5}}, "Taux réel → consommation (0 / 0,5)"),
    "rigidite": ({"surcharges": {"ASYM_SALAIRES": 1.0}}, {"surcharges": {"ASYM_SALAIRES": 0.25}}, "Rigidité salariale à la baisse (aucune / forte)"),
    "transfert_benefices": ({"surcharges": {"SEMI_ELAST_IS": 0.2}}, {"surcharges": {"SEMI_ELAST_IS": 1.5}}, "Transfert de bénéfices (0,2 / 1,5)"),
    "tresorerie": ({"surcharges": {"THETA_TRESORERIE": 0.0}}, {"surcharges": {"THETA_TRESORERIE": 0.3}}, "Trésorerie → investissement (0 / 0,3)"),
    "offre_travail": ({"niveaux_mesures": {"offre_travail": "basse"}}, {"niveaux_mesures": {"offre_travail": "haute"}}, "Élasticités d'offre de travail (basses / hautes)"),
    "incidence": ({"niveaux_mesures": {"incidence": "basse"}}, {"niveaux_mesures": {"incidence": "haute"}}, "Incidence salariale des prélèvements (basse / haute)"),
    "assurance_chomage": ({"niveaux_mesures": {"ac": "basse"}}, {"niveaux_mesures": {"ac": "haute"}}, "Assurance chômage → chômage structurel (0 / 0,13)"),
}


def run(cur, hyp):
    sc = {"nom": "s", "horizon": 2047, "hypotheses": {"europe": False, "incertitude": 0, "profils": False, "distribution_dynamique": False, **hyp},
          "mesures": [SIM.CUR[a]["mesure"](v) for a, v in cur.items()]}
    tr = X.executer(X.depuis_curseurs(sc))["trajectoires"]
    return {k: {t: tr[k]["ecart"][t] for t in (2030, 2035, 2040, 2047)} for k in ("pib", "chomage", "solde_pib", "dette_pib", "pib_potentiel")}


if __name__ == "__main__":
    P = SV.programmes()
    for k in sys.argv[1:]:
        f = OUT / f"sensibilite_{k}.json"
        res = {k: json.loads(f.read_text())} if f.exists() else {k: {}}
        if "central" not in res[k]:
            res[k]["central"] = run(P[k], {})
        for p, (lo, hi, lib) in PARAMS.items():
            if p in res[k]:
                continue
            t0 = time.time()
            res[k][p] = {"libelle": lib, "basse": run(P[k], lo), "haute": run(P[k], hi)}
            f.write_text(json.dumps(res[k], default=float))
            print(k, p, round(time.time() - t0), round(res[k][p]["basse"]["dette_pib"][2047], 1), round(res[k][p]["haute"]["dette_pib"][2047], 1), flush=True)
