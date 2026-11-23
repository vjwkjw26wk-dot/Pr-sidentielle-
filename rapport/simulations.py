"""Simulations du rapport (version 0.6) : expériences isolées, interactions, scénarios.

Chaque expérience est un jeu de curseurs du simulateur (mesures en vigueur en 2028, horizon 2047, rétroactions de la zone
euro, trajectoire de référence « politique inchangée »), simulée par le modèle complet (simulateur/executer.py) avec la
microsimulation pour les mesures socio-fiscales. Sortie : rapport/resultats/experiences_<lot>.json
Usage : python3 rapport/simulations.py <lot> [<lot> ...]   (lots : voir LOTS)
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "src"))
from simulateur import executer as X, catalogue as CAT  # noqa: E402

HORIZON = 2047
CUR = {c["cle"]: c for c in CAT.CURSEURS}
SORTIE = RACINE / "rapport" / "resultats"
SORTIE.mkdir(parents=True, exist_ok=True)

# Expériences : (lot, nom, libellé, curseurs). Montants choisis pour un rendement ou un coût ex ante d'environ 10 Md€
# quand c'est possible (comparabilité).
EXPERIENCES = [
    # 1. Impôts (environ +10 Md€ ex ante)
    ("impots", "ir_bas", "Impôt sur le revenu : 1re tranche +2 points", {"ir_t1": 13}),
    ("impots", "ir_haut", "Impôt sur le revenu : tranche supérieure +10 points", {"ir_t4": 55}),
    ("impots", "csg", "CSG sur les revenus d'activité +1 point", {"csg_activite": 1}),
    ("impots", "tva", "TVA, taux normal +1 point", {"tva": 1}),
    ("impots", "isf", "Impôt sur la fortune, taux moyen 1 %", {"isf": 1.0}),
    ("impots", "pfu", "Prélèvement forfaitaire unique +15 points", {"pfu": 15}),
    ("impots", "is", "Impôt sur les sociétés de 25,8 % à 30,5 %", {"taux_is": 30.5}),
    ("impots", "production", "Impôts de production +10 Md€", {"impots_production": 10}),
    ("impots", "cotisations", "Cotisations employeurs +10 Md€", {"cotisations_employeurs": 10}),
    ("impots", "successions", "Droits de succession +50 %", {"successions": 50}),
    ("impots", "carbone", "Taxe carbone +50 € par tonne", {"taxe_carbone": 50}),
    # 2. Salaires
    ("salaires", "sal2", "Salaires +2 % (hausse générale)", {"salaires": 2}),
    ("salaires", "sal5", "Salaires +5 % (hausse générale)", {"salaires": 5}),
    ("salaires", "smic5", "SMIC +5 % (coup de pouce)", {"smic": 5}),
    ("salaires", "smic10", "SMIC +10 % (coup de pouce)", {"smic": 10}),
    ("salaires", "point3", "Point d'indice de la fonction publique +3 %", {"point_indice": 3}),
    # 3. Dépenses (environ −10 Md€)
    ("depenses", "emploi_public", "Emplois publics −170 000 (en 5 ans)", {"emploi_public": -170}),
    ("depenses", "fonctionnement", "Autres dépenses de fonctionnement −10 Md€", {"autres_depenses": -10}),
    ("depenses", "sante", "Dépenses de santé −10 Md€", {"sante": -10}),
    ("depenses", "education", "Dépenses d'éducation −10 Md€", {"education": -10}),
    ("depenses", "defense", "Dépenses de défense −10 Md€", {"defense": -10}),
    ("depenses", "invest_public_moins", "Investissement public −10 Md€", {"investissement_public": -10}),
    ("depenses", "indexation", "Pensions : sous-indexation de 1 point par an", {"indexation_pensions": -1}),
    ("depenses", "chomage", "Allocations chômage −25 %", {"assurance_chomage": -25}),
    ("depenses", "prestations_moins", "Prestations familiales et logement −10 %", {"allocations_familiales": -10, "aides_logement": -10}),
    ("depenses", "transferts_moins", "Transferts aux ménages −0,3 point de PIB", {"transferts_menages": -0.3}),
    # 4. Cotisations
    ("cotisations", "cot_moins10", "Cotisations employeurs −10 Md€", {"cotisations_employeurs": -10}),
    ("cotisations", "cot_moins20", "Cotisations employeurs −20 Md€", {"cotisations_employeurs": -20}),
    ("cotisations", "tva_sociale", "Cotisations employeurs −20 Md€ financées par la TVA (+2,4 points)", {"cotisations_employeurs": -20, "tva": 2.4}),
    # 5. Investissement
    ("investissement", "invest_public10", "Investissement public +10 Md€", {"investissement_public": 10}),
    ("investissement", "invest_public30", "Investissement public +30 Md€", {"investissement_public": 30}),
    ("investissement", "is_baisse", "Impôt sur les sociétés à 20 % (incitation à l'investissement privé)", {"taux_is": 20}),
    ("investissement", "logements_sociaux", "Logements sociaux +50 000 par an", {"logements_sociaux": 50}),
    # 6. Réindustrialisation
    ("industrie", "reindus10", "Réindustrialisation : −10 % d'importations dans huit produits industriels (5 ans, investissement, surcoût)", {"reindustrialisation": 10}),
    ("industrie", "reindus20", "Réindustrialisation : −20 %", {"reindustrialisation": 20}),
    ("industrie", "reindus10_energie", "Réindustrialisation −10 % avec énergie importée +20 %", {"reindustrialisation": 10, "energie_import": 20}),
    ("industrie", "douanes10", "Droits de douane de 10 % sur les importations hors UE", {"droits_douane": 10}),
    # 7. Prestations
    ("prestations", "rsa25", "RSA +25 %", {"rsa": 25}),
    ("prestations", "ppa25", "Prime d'activité +25 %", {"prime_activite": 25}),
    ("prestations", "af25", "Allocations familiales +25 %", {"allocations_familiales": 25}),
    ("prestations", "apl_moins10", "Aides au logement −10 %", {"aides_logement": -10}),
    ("prestations", "aspa25", "Minimum vieillesse +25 %", {"minimum_vieillesse": 25}),
    # 8. Temps de travail et carrière
    ("travail", "temps37", "Durée du travail 37 heures", {"temps_travail": 37}),
    ("travail", "temps32", "Durée du travail 32 heures", {"temps_travail": 32}),
    ("travail", "age65", "Âge légal 65 ans (progressif)", {"age_legal": 65}),
    ("travail", "age66", "Âge légal 66 ans (progressif)", {"age_legal": 66}),
    ("travail", "age62", "Âge légal 62 ans (progressif)", {"age_legal": 62}),
    # Complémentaires
    ("complementaires", "energie50", "Prix de l'énergie importée +50 %", {"energie_import": 50}),
    ("complementaires", "energie_moins20", "Prix de l'énergie importée −20 %", {"energie_import": -20}),
    ("complementaires", "tva_reduite", "TVA à taux réduits +2 points", {"tva_reduite": 2}),
    ("complementaires", "transferts_plus", "Transferts aux ménages +0,3 point de PIB", {"transferts_menages": 0.3}),
    # Interactions
    ("interactions", "combi_cot_tva", "TVA, taux normal +2,4 points (seule)", {"tva": 2.4}),
    ("interactions", "combi_invest_age", "Investissement public +20 Md€ et âge légal 65 ans", {"investissement_public": 20, "age_legal": 65}),
    ("interactions", "invest20", "Investissement public +20 Md€ (seul)", {"investissement_public": 20}),
    ("interactions", "combi_rsa_ppa_csg", "RSA +25 %, prime d'activité +25 %, financés par la CSG (+0,5 point)", {"rsa": 25, "prime_activite": 25, "csg_activite": 0.5}),
    ("interactions", "csg05", "CSG +0,5 point (seule)", {"csg_activite": 0.5}),
    ("interactions", "combi_reindus_douane", "Réindustrialisation −10 % et droits de douane 10 %", {"reindustrialisation": 10, "droits_douane": 10}),
    ("interactions", "combi_emploipub_fonct", "Emplois publics −170 000 et fonctionnement −10 Md€", {"emploi_public": -170, "autres_depenses": -10}),
]
INDIC = ["pib", "croissance", "emploi", "chomage", "inflation", "rdb", "taux_epargne", "solde_exterieur_pib", "solde_pib", "dette_pib",
         "recettes_pib", "depenses_pib", "interets_pib", "rnb", "part_industrie", "pensions_pib", "x", "m", "fbcf", "c", "salaire", "pc",
         "productivite", "population_active"]


def simuler(nom, curseurs, horizon=HORIZON, hyp=None):
    sc = {"nom": nom, "horizon": horizon, "hypotheses": {"europe": True, "incertitude": 0, "profils": False, **(hyp or {})},
          "mesures": [CUR[k]["mesure"](v) for k, v in curseurs.items()]}
    r = X.executer(X.depuis_curseurs(sc))
    tr = r["trajectoires"]
    out = {"curseurs": curseurs, "inegalites": r.get("inegalites"), "distribution": r.get("distribution"),
           "statique": r.get("statique"), "comportements": r.get("comportements"), "traj": {}}
    for k in INDIC:
        if k in tr:
            out["traj"][k] = {s: {int(t): float(v) for t, v in tr[k][s].items()} for s in ("scenario", "reference", "ecart") if s in tr[k]}
    return out


def main(lots):
    for lot in lots:
        res = {}
        for l, nom, lib, cur in EXPERIENCES:
            if l != lot:
                continue
            t0 = time.time()
            try:
                res[nom] = {"libelle": lib, **simuler(nom, cur)}
            except Exception as e:  # noqa: BLE001
                res[nom] = {"libelle": lib, "erreur": repr(e)}
            print(lot, nom, round(time.time() - t0), flush=True)
        (SORTIE / f"experiences_{lot}.json").write_text(json.dumps(res, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main(sys.argv[1:])
