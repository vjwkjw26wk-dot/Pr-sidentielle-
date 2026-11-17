"""Catalogue des mesures simulables (version 0.1).

Chaque mesure : libellé, paramètres (unité, bornes), modules mobilisés, niveau de preuve des mécanismes principaux
(échelle du cahier des charges : A observé, B estimé, C issu de modèles documentés, D hypothèse, E exploratoire),
limites propres. La traduction en entrées des modèles est faite par `appliquer` (M8, M9, M10).
Neutralité : chaque mesure passe par les mêmes modèles, conventions et indicateurs, quelle que soit son origine.
"""
from __future__ import annotations

MESURES = {
    "depense_publique": {
        "libelle": "Consommation publique (dépenses de fonctionnement et emploi publics)",
        "parametres": {"points_pib": "variation en points de PIB (−3 à +3)", "debut": "première année d'application"},
        "modules": ["M8", "M11"], "preuve": "B (équations estimées), D (fermeture d'offre)",
        "limites": "Composition par fonction non distinguée ; multiplicateur de première année au-dessus des références (1,4 contre 0,8-1,3)."},
    "taux_is": {
        "libelle": "Taux normal de l'impôt sur les sociétés",
        "parametres": {"taux": "taux en % (15 à 40)", "debut": "première année"},
        "modules": ["M8"], "preuve": "B fragile (élasticité de l'investissement au coût d'usage estimée sur 23 observations)",
        "limites": "Pas d'effet sur la localisation des profits ni sur les prix ; recette d'IS proportionnelle à l'excédent des branches."},
    "bareme_ir": {
        "libelle": "Barème de l'impôt sur le revenu (taux et seuils des tranches, décote, plafond du quotient familial)",
        "parametres": {"taux": "taux par tranche, ex. {1: 0.14}", "seuils_facteur": "facteur appliqué aux seuils (ex. 0.98)",
                       "decote_facteur": "facteur sur les seuils de décote", "plafond_qf_facteur": "facteur sur le plafond du quotient familial"},
        "modules": ["M4", "M10", "M8"], "preuve": "A (législation, OpenFisca), B (comportements macroéconomiques)",
        "limites": "Effet statique ; sensibilité aux seuils inférieure d'environ 15 % à un calcul direct ; 3 M de foyers hors champ."},
    "rsa": {
        "libelle": "Montant forfaitaire du RSA",
        "parametres": {"facteur": "facteur sur le montant (ex. 1.10)"},
        "modules": ["M4", "M10", "M8"], "preuve": "A (législation), B (recours apparent mesuré)",
        "limites": "Non-recours supposé inchangé ; erreur d'échantillonnage d'environ 2 %."},
    "prime_activite": {
        "libelle": "Montant forfaitaire de la prime d'activité",
        "parametres": {"facteur": "facteur sur le montant"},
        "modules": ["M4", "M10", "M8"], "preuve": "A (législation), B",
        "limites": "Éligibles sous-estimés d'environ 25 % : effet probablement sous-estimé."},
    "allocations_familiales": {
        "libelle": "Base mensuelle des allocations familiales (BMAF)",
        "parametres": {"facteur": "facteur sur la BMAF"},
        "modules": ["M4", "M10", "M8"], "preuve": "A", "limites": "La BMAF sert aussi à d'autres prestations non simulées."},
    "age_legal": {
        "libelle": "Âge d'ouverture des droits à la retraite",
        "parametres": {"regle": "\"2010\" (62 ans), \"2023\" (loi de 2023 sans suspension), ou âge cible (ex. \"65\")"},
        "modules": ["M1", "M9", "M8"], "preuve": "B (activité des seniors estimée, hors échantillon 2020-2025), D (fermeture d'offre)",
        "limites": "Pas de durée d'assurance, décote, surcote, réversion ni distinction des régimes."},
    "transferts_menages": {
        "libelle": "Transferts monétaires aux ménages (non ciblés)",
        "parametres": {"points_pib": "variation en points de PIB", "debut": "première année"},
        "modules": ["M8", "M11"], "preuve": "B", "limites": "Pas de ciblage : effet distributif non calculé (utiliser une mesure de M4)."},
    "energie_import": {
        "libelle": "Choc de prix de l'énergie importée (environnement, non une mesure)",
        "parametres": {"hausse": "hausse relative (ex. 0.2)", "debut": "première année"},
        "modules": ["M5", "M8"], "preuve": "A (tableaux entrées-sorties), B (transmission estimée)",
        "limites": "Pas de substitution entre énergies ; tarifs réglementés non représentés."},
    "reindustrialisation": {
        "libelle": "Objectif de substitution d'importations industrielles",
        "parametres": {"baisse_parts_importees": "baisse relative des parts importées (ex. 0.10)", "produits": "liste de produits A64",
                       "duree": "années de montée en charge", "surcout": "surcoût de la valeur ajoutée produite en France"},
        "modules": ["M5", "M8"], "preuve": "D (l'objectif de substitution est une hypothèse, pas un résultat)",
        "limites": "Le moyen d'atteindre l'objectif (aides, droits de douane, compétitivité) n'est pas modélisé ; coût budgétaire à ajouter."},
    "salaires": {
        "libelle": "Hausse générale des salaires (choc ponctuel)",
        "parametres": {"hausse": "hausse relative la première année", "debut": "année"},
        "modules": ["M8"], "preuve": "B", "limites": "Pas de distinction SMIC / autres salaires ; pas d'effet sur la prime d'activité."},
}

INDUSTRIE_DEFAUT = ["CPA_C20", "CPA_C21", "CPA_C24", "CPA_C25", "CPA_C26", "CPA_C27", "CPA_C28", "CPA_C29"]


def reforme_openfisca(mesures: list) -> tuple[dict | None, tuple]:
    """Réforme paramétrique OpenFisca et blocs à recalculer (impôt, prestations) pour les mesures de M4."""
    par, calc = {}, set()
    for m in mesures:
        t, p = m["type"], m.get("parametres", {})
        if t == "bareme_ir":
            for i, v in (p.get("taux") or {}).items():
                par[f"impot_revenu.bareme_ir_depuis_1945.bareme.brackets[{int(i)}].rate"] = float(v)
            if p.get("seuils_facteur"):
                for i in (1, 2, 3, 4):
                    par[f"impot_revenu.bareme_ir_depuis_1945.bareme.brackets[{i}].threshold"] = {"facteur": float(p["seuils_facteur"])}
            if p.get("decote_facteur"):
                for k in ("seuil_celib", "seuil_couple"):
                    par[f"impot_revenu.calcul_impot_revenu.plaf_qf.decote.{k}"] = {"facteur": float(p["decote_facteur"])}
            if p.get("plafond_qf_facteur"):
                par["impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part.general"] = {"facteur": float(p["plafond_qf_facteur"])}
            calc.add("ir")
        elif t == "rsa":
            par["prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa"] = {"facteur": float(p["facteur"]), "debut": "2024-10-01"}
            calc.add("prest")
        elif t == "prime_activite":
            par["prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m.montant_de_base"] = {"facteur": float(p["facteur"]), "debut": "2024-10-01"}
            calc.add("prest")
        elif t == "allocations_familiales":
            par["prestations_sociales.prestations_familiales.bmaf.bmaf"] = {"facteur": float(p["facteur"]), "debut": "2024-10-01"}
            calc.add("prest")
    return ({"debut": "2024-01-01", "parametres": par} if par else None), tuple(sorted(calc))
