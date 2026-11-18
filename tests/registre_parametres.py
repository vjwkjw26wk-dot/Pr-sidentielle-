"""Registre des paramètres et de leurs incertitudes (version 0.6).

Produit outputs/registre_parametres.csv et doc/14_registre_parametres.md : pour chaque paramètre important, valeur
centrale, catégorie (E estimé sur données françaises, C calibré sur données françaises, L transposé de la littérature,
H hypothèse conventionnelle), source, méthode, période, erreur-type, niveau de confiance, plage plausible, équations
et résultats qui en dépendent ; corrélations fortes entre coefficients estimés d'une même équation.
Usage : python3 tests/registre_parametres.py
"""
from __future__ import annotations

import csv
import pathlib
import sys

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE))
import m8_modele as M  # noqa: E402
import m7_equations as E  # noqa: E402
import m13_comportements as B13  # noqa: E402
import m14_heterogeneite as H14  # noqa: E402
from simulateur import executer as X  # noqa: E402

COEFS = {   # coefficients estimés suivis : (équation, coefficient, libellé, dépendances)
    ("consommation", "dlrdb"): ("Consommation : élasticité de court terme au RDB réel", "multiplicateurs, toutes mesures sur les ménages"),
    ("consommation", "ecart_1"): ("Consommation : force de rappel", "effets de moyen terme, épargne"),
    ("importations", "dld"): ("Importations : élasticité de court terme à la demande", "fuites, multiplicateurs, solde extérieur"),
    ("importations", "dlprel"): ("Importations : élasticité-prix de court terme", "compétitivité, salaires, TVA"),
    ("importations", "lprel_1"): ("Importations : prix relatif de long terme", "compétitivité"),
    ("importations", "lm_1"): ("Importations : rappel", "dynamique des importations"),
    ("exportations", "dldm"): ("Exportations : élasticité à la demande mondiale", "trajectoire de référence, Europe"),
    ("exportations", "dlprel"): ("Exportations : élasticité-prix", "salaires, cotisations, prix"),
    ("investissement_snf", "dlq"): ("Investissement des SNF : accélérateur", "multiplicateurs"),
    ("investissement_snf", "ecm_1"): ("Investissement des SNF : rappel", "investissement de moyen terme"),
    ("investissement_snf", "lcu_1"): ("Investissement des SNF : coût d'usage du capital", "IS, taux d'intérêt"),
    ("investissement", "dlq"): ("Investissement par branche : accélérateur", "investissement sectoriel"),
    ("salaires", "dlpc"): ("Salaires : indexation de court terme", "boucle prix-salaires, inflation"),
    ("salaires", "ecm_1"): ("Salaires : rappel vers la part salariale", "partage de la valeur ajoutée"),
    ("prix_va", "dlclu"): ("Prix de VA : transmission du coût salarial unitaire", "compétitivité, inflation, salaires"),
    ("prix_va", "ecm_1"): ("Prix de VA : rappel", "marges"),
    ("prix_va", "tucd"): ("Prix de VA : tension des capacités", "contraintes d'offre"),
    ("emploi", "dlq"): ("Emploi : élasticité de court terme à la production", "emploi, chômage"),
    ("emploi", "ecm_1"): ("Emploi : rappel", "emploi de moyen terme"),
    ("logement", "dlrdb"): ("Logement des ménages : élasticité au revenu", "investissement, multiplicateurs"),
    ("logement", "ecart_1"): ("Logement des ménages : rappel", "investissement des ménages"),
    ("transmission", "dlpm"): ("Transmission des prix d'importation (année même)", "chocs énergétiques, inflation"),
    ("revenus_d4", "dpibn"): ("Revenus de la propriété des ménages : élasticité au PIB nominal", "RDB"),
    ("revenus_ebe", "dpibn"): ("Revenu mixte et EBE des ménages : élasticité au PIB nominal", "RDB"),
}

AUTRES = [  # (paramètre, valeur, catégorie, source, méthode, période, confiance, plage, dépendances)
    ("Courbe de Phillips (E.PHILLIPS)", E.PHILLIPS, "C", "DG Trésor (Mésange), Insee ; non identifiée sur données annuelles 1997-2019", "calibrage", "—", "faible", "−0,008 à −0,002", "salaires, prix, chômage, dette (effet dénominateur)"),
    ("Élasticité de substitution capital-travail (SIGMA_TRAVAIL)", E.SIGMA_TRAVAIL, "L", "Cette, Lecat, Ly-Marin (2016) ; littérature 0,2-0,7", "transposition", "—", "faible", "0,2 à 0,7", "emploi après choc de coût du travail"),
    ("Fermeture d'offre (RHO_DEFAUT)", M.RHO_DEFAUT, "H", "hypothèse (politique monétaire, crédit, compétitivité agrégés)", "convention", "—", "faible", "0 à 0,4", "multiplicateurs de moyen terme, tous scénarios"),
    ("Loi d'Okun (OKUN)", M.OKUN, "L", "estimations françaises de la loi d'Okun", "transposition", "—", "moyenne", "1,2 à 2", "fermeture d'offre"),
    ("Délai de construction des capacités (DELAI_CAPACITES)", M.DELAI_CAPACITES, "H", "ordre de grandeur des projets industriels", "convention", "—", "faible", "1 à 4 ans", "réindustrialisation"),
    ("Profil des propensions à consommer par décile", "0,90 … 0,40", "L", "Jappelli-Pistaferri (2014), Fagereng et al. (2021) ; cohérence Insee Focus 338", "transposition", "—", "faible", "profil plat à accentué", "mesures redistributives"),
    ("Propension du dernier centile (PMC_TOP1)", H14.PMC_TOP1, "L", "littérature", "transposition", "—", "faible", "0,1 à 0,5", "dividendes, ISF, PFU"),
    ("Part distribuée des profits supplémentaires", H14.DISTRIBUTION_PROFITS["central"], "L", "France Stratégie (2019-2023) ; littérature sur l'IS", "transposition", "—", "faible", "0,3 à 0,7", "IS, impôts de production"),
    ("Part des dividendes aux non-résidents", H14.PART_NON_RESIDENTS, "C", "Banque de France (CAC 40 : 50 % ; actions cotées : 36,7 % en 2022 ; hors CAC 40 : environ 30 % ; non cotées : moins)", "calibrage", "2022-2024", "moyenne", "0,20 à 0,50", "RNB après baisse d'IS"),
    ("Part des dividendes résidents reçue par les ménages", H14.PART_MENAGES_DIVIDENDES, "C", "comptes de secteurs 2022 (D42 ménages / D42 versés nets)", "calibrage", "2022", "faible", "0,2 à 0,5", "RDB après baisse d'IS"),
    ("Élasticité du revenu imposable (M13)", B13.ELASTICITE_REVENU["centrale"], "L", "Saez, Slemrod, Giertz (2012) ; Lefebvre et al. (France)", "transposition", "—", "moyenne", "0,1 à 0,4", "rendement des hausses d'IR sur les hauts revenus"),
    ("Élasticité des revenus du capital (M13)", B13.ELASTICITE_CAPITAL["centrale"], "L", "France Stratégie (PFU)", "transposition", "—", "moyenne", "0,2 à 1", "PFU, dividendes"),
    ("Perte d'assiette de l'ISF (M13)", B13.ISF["centrale"], "L", "littérature (Pichet, Zucman, Garbinti)", "transposition", "—", "faible", "0,1 à 0,5", "rendement ISF"),
    ("Élasticité de la production au capital public", X.ELAST_CAPITAL_PUBLIC, "L", "Bom et Ligthart (2014)", "méta-analyse", "—", "moyenne", "0,04 à 0,12", "investissement public de long terme"),
    ("Coût public d'un point de SMIC", X.COUT_PUBLIC_POINT_SMIC, "C", "Institut Montaigne ; allègements généraux", "calibrage", "2025", "moyenne", "500 à 800 M€", "SMIC"),
    ("Diffusion du SMIC au salaire moyen", X.PART_SMIC_DIFFUSION, "H", "ordre de grandeur (Insee, DARES)", "convention", "—", "faible", "0,05 à 0,2", "SMIC"),
    ("Répercussion de la TVA sur les prix", X.REPERCUSSION_TVA, "L", "Benzarti et al. ; IPP", "transposition", "—", "moyenne", "0,6 à 1", "TVA"),
    ("Répercussion des impôts de production", X.REPERCUSSION_IMPOTS_PRODUCTION, "H", "hypothèse", "convention", "—", "faible", "0,2 à 0,8", "impôts de production"),
    ("Compensation horaire des 32 heures", X.COMPENSATION_PRODUCTIVITE_HORAIRE, "H", "bilan des 35 heures (DARES, Insee)", "convention", "—", "faible", "0,5 à 0,9", "temps de travail"),
    ("Coefficient de pension marginale", 0.55, "C", "chiffrage officiel de l'abrogation (14,1 Md€ en 2030)", "calibrage", "2025", "moyenne", "0,45 à 0,7", "âge légal"),
    ("Taux d'épargne cible de la référence", "17,9 → 15,5 %", "H", "PLF 2027 (17,3 % en 2027), moyenne avant 2020", "convention", "2025-2031", "faible", "14 à 18 % en 2031", "trajectoire de référence (niveaux), peu les écarts"),
    ("Rétroactions zone euro (THETA_PRIME, etc.)", "M11", "C", "M11", "calibrage", "—", "faible", "0 à 2 × central", "taux, demande des partenaires"),
]


def confiance(t):
    return "élevée" if abs(t) >= 3 else ("moyenne" if abs(t) >= 2 else "faible")


def main():
    mod = M.Modele(2022)
    lignes = []
    for (eq, coef), (lib, dep) in COEFS.items():
        e = mod.eq[eq]
        r = e.res
        v, se = float(r.params[coef]), float(r.bse[coef])
        t = v / se if se else np.inf
        per = f"{int(r.model.data.row_labels.min()) if hasattr(r.model.data, 'row_labels') and r.model.data.row_labels is not None and np.issubdtype(type(r.model.data.row_labels.min()), np.integer) else 1997}-2019"
        lignes.append({"parametre": lib, "equation": f"{eq}.{coef}", "valeur": round(v, 4), "categorie": "E",
                       "source": "Eurostat, Insee (comptes nationaux annuels)", "methode": "MCO" + (" (panel 25 branches)" if eq in ("emploi", "prix_va", "investissement") else ""),
                       "periode": "1997-2019" if eq != "transmission" else "1998-2024", "erreur_type": round(se, 4), "t": round(t, 1),
                       "confiance": confiance(t), "plage": f"{v - 2 * se:.3f} à {v + 2 * se:.3f} (± 2 e.-t.)", "depend": dep, "n": int(r.nobs)})
    for p, v, cat, src, meth, per, conf, plage, dep in AUTRES:
        lignes.append({"parametre": p, "equation": "—", "valeur": v, "categorie": cat, "source": src, "methode": meth, "periode": per,
                       "erreur_type": "—", "t": "—", "confiance": conf, "plage": plage, "depend": dep, "n": "—"})
    # corrélations fortes entre coefficients estimés
    corr = []
    for eq in ("consommation", "importations", "exportations", "investissement_snf", "salaires", "logement", "transmission", "revenus_d4"):
        r = mod.eq[eq].res
        C = np.asarray(r.cov_params())
        d = np.sqrt(np.diag(C))
        R = C / np.outer(d, d)
        names = list(r.params.index)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if abs(R[i, j]) >= 0.7 and "const" not in (names[i], names[j]):
                    corr.append((eq, names[i], names[j], R[i, j]))
    f = RACINE / "outputs" / "registre_parametres.csv"
    with f.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    L = ["# Registre des paramètres et incertitudes (version 0.6)", "",
         "Généré par tests/registre_parametres.py (fichier réutilisable : outputs/registre_parametres.csv). Catégories : "
         "**E** estimé sur données françaises ; **C** calibré sur données françaises ; **L** transposé de la littérature ; "
         "**H** hypothèse conventionnelle. Confiance pour E : élevée si |t| ≥ 3, moyenne si 2 ≤ |t| < 3, faible sinon. "
         "Une erreur-type faible ne garantit pas l'absence de biais de spécification (simultanéité, variables omises, "
         "rupture) : la confiance indiquée est statistique.", "",
         "| Paramètre | Équation | Valeur | Cat. | Méthode, période (n) | Erreur-type (t) | Confiance | Plage | Dépendances |",
         "|---|---|---|---|---|---|---|---|---|"]
    for l in lignes:
        L.append(f"| {l['parametre']} | {l['equation']} | {l['valeur']} | {l['categorie']} | {l['methode']}, {l['periode']} ({l['n']}) | "
                 f"{l['erreur_type']} ({l['t']}) | {l['confiance']} | {l['plage']} | {l['depend']} |")
    L += ["", "## Coefficients fortement corrélés (|ρ| ≥ 0,7, même équation)", "",
          "Ces paires sont mal identifiées séparément : leurs effets peuvent se compenser ; les tirages statistiques conjoints "
          "(tests/contre_expertise.py) en tiennent compte, les sensibilités univariées non.", "",
          "| Équation | Coefficient 1 | Coefficient 2 | ρ |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {r:+.2f} |" for a, b, c, r in corr]
    L += ["", "Sources principales : voir doc/12_audit_mecanismes.md (section 8) et doc/13_contre_expertise.md."]
    (RACINE / "doc" / "14_registre_parametres.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(lignes)} paramètres, {len(corr)} corrélations fortes")


if __name__ == "__main__":
    main()
