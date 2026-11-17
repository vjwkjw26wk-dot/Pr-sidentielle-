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


# ------------------------------------------------------------------------------------------------------------------
# Mesures ajoutées (version 0.3, novembre 2026)
# ------------------------------------------------------------------------------------------------------------------
MESURES.update({
    "csg": {
        "libelle": "Taux de la CSG (revenus d'activité ; pensions au taux plein)",
        "parametres": {"activite_points": "variation du taux sur les revenus d'activité (points)",
                       "retraite_points": "variation du taux plein sur les pensions (points)", "debut": "année"},
        "modules": ["M4", "M10", "M8"], "preuve": "A (barème), B (assiettes reconstituées et calées sur les totaux nationaux)",
        "limites": "Assiettes approchées à partir des revenus imposables ; revenus du patrimoine et revenus non salariaux hors distribution."},
    "pfu": {
        "libelle": "Prélèvement forfaitaire unique sur les revenus du capital (part impôt sur le revenu)",
        "parametres": {"points": "variation du taux (points)", "debut": "année"},
        "modules": ["M8", "M13"], "preuve": "B (assiette agrégée), D (répartition, comportements)",
        "limites": "Assiette agrégée (environ 60 Md€) ; répartition approchée sur le décile supérieur ; forte réaction des distributions de dividendes."},
    "isf": {
        "libelle": "Impôt sur la fortune (remplace l'IFI)",
        "parametres": {"taux_moyen": "taux moyen effectif sur le patrimoine net taxable au-delà de 1,3 M€ (%)", "debut": "année"},
        "modules": ["M8", "M13"], "preuve": "C (assiette reconstituée à partir de l'ISF 2017), D (comportements, départs)",
        "limites": "Assiette agrégée ; évasion et départs selon des élasticités de la littérature (fourchette large)."},
    "successions": {
        "libelle": "Droits de succession et de donation",
        "parametres": {"variation": "variation relative du rendement (ex. 0.2)", "debut": "année"},
        "modules": ["M8", "M13"], "preuve": "B (rendement observé), D (comportements)",
        "limites": "Pas de répartition par décile de niveau de vie (impôt sur le patrimoine transmis)."},
    "tva": {
        "libelle": "Taux normal de TVA",
        "parametres": {"points": "variation du taux normal (points)", "debut": "année"},
        "modules": ["M8"], "preuve": "B (rendement), D (répercussion sur les prix : 80 %, répartition selon la consommation)",
        "limites": "Taux réduits non distingués ; répartition par décile selon la structure de consommation par quintile (enquête Budget des familles 2015, Eurostat)."},
    "taxe_carbone": {
        "libelle": "Composante carbone des taxes sur l'énergie",
        "parametres": {"euros_tonne": "hausse en euros par tonne de CO2", "debut": "année"},
        "modules": ["M8"], "preuve": "B (rendement), D (répercussion, répartition)",
        "limites": "Pas de baisse des émissions ni de substitution modélisées ; pas de redistribution du produit sauf mesure ajoutée."},
    "cotisations_employeurs": {
        "libelle": "Cotisations sociales patronales (allègements généraux)",
        "parametres": {"md": "variation des cotisations en Md€ (négatif : baisse)", "debut": "année"},
        "modules": ["M8"], "preuve": "B (équations d'emploi et de prix), D (ciblage sur les bas salaires non distingué)",
        "limites": "Effet moyen : le ciblage sur les bas salaires, où l'emploi réagit davantage, n'est pas représenté."},
    "smic": {
        "libelle": "Revalorisation du SMIC (au-delà de la règle)",
        "parametres": {"hausse": "hausse relative (ex. 0.05)", "debut": "année"},
        "modules": ["M8"], "preuve": "D (diffusion : 11 % de la masse salariale concernée, hypothèse)",
        "limites": "Pas d'effet spécifique sur l'emploi peu qualifié ni sur la prime d'activité ; effet distributif non calculé."},
    "point_indice": {
        "libelle": "Point d'indice de la fonction publique",
        "parametres": {"hausse": "hausse relative (ex. 0.03)", "debut": "année"},
        "modules": ["M8"], "preuve": "A (masse salariale publique), B", "limites": "Effet distributif non calculé."},
    "emploi_public": {
        "libelle": "Emplois publics supplémentaires",
        "parametres": {"milliers": "nombre d'agents (milliers)", "debut": "année"},
        "modules": ["M8", "M11"], "preuve": "B", "limites": "Coût moyen de 56 000 € par agent ; effets sur la qualité des services non mesurés."},
    "investissement_public": {
        "libelle": "Investissement public",
        "parametres": {"md": "Md€ par an", "debut": "année"},
        "modules": ["M8", "M11"], "preuve": "B (effet de demande)",
        "limites": "Effet sur la productivité de long terme non modélisé (sous-estimation probable à long terme)."},
    "depense_fonction": {
        "libelle": "Dépenses de fonctionnement par fonction (santé, éducation, défense, autres)",
        "parametres": {"fonction": "santé | éducation | défense | autres", "md": "Md€ par an", "debut": "année"},
        "modules": ["M8", "M11"], "preuve": "B, D (composition non distinguée dans le modèle)",
        "limites": "Toutes les fonctions ont le même contenu en importations et le même effet ; effets sur la santé ou l'éducation non mesurés."},
    "assurance_chomage": {
        "libelle": "Générosité de l'assurance chômage",
        "parametres": {"variation": "variation relative des allocations (ex. -0.1)", "debut": "année"},
        "modules": ["M8"], "preuve": "B (dépense), D (effet sur le chômage structurel : 0,1 point pour 10 %, fourchette 0-0,3)",
        "limites": "Paramètres (durée, taux de remplacement) non distingués ; effet distributif non calculé."},
    "minimum_vieillesse": {
        "libelle": "Minimum vieillesse (ASPA)",
        "parametres": {"hausse": "hausse relative", "debut": "année"},
        "modules": ["M8"], "preuve": "A (dépense 2024 : 4,1 Md€), D (non-recours inchangé)",
        "limites": "Répartition par décile approchée (premier et deuxième déciles)."},
    "indexation_pensions": {
        "libelle": "Indexation des pensions (écart annuel à l'inflation)",
        "parametres": {"points": "points par an (négatif : sous-indexation)", "duree": "nombre d'années", "debut": "année"},
        "modules": ["M9", "M8"], "preuve": "A (règle), B (masse des pensions par génération)",
        "limites": "Toutes les pensions de droit direct concernées, sans seuil de protection des petites pensions."},
    "aides_logement": {
        "libelle": "Aides personnelles au logement",
        "parametres": {"facteur": "facteur sur les montants versés"},
        "modules": ["M4", "M10", "M8"], "preuve": "A (montants calculés par OpenFisca), D (variation proportionnelle des montants)",
        "limites": "Variation proportionnelle des aides calculées : pas d'entrée ni de sortie d'éligibilité ; effet sur les loyers non modélisé."},
    "temps_travail": {
        "libelle": "Durée légale du travail",
        "parametres": {"heures": "durée hebdomadaire (35 actuellement)", "debut": "année", "montee": "années de mise en place"},
        "modules": ["M8"], "preuve": "D (70 % de la baisse absorbée sans embauche — productivité horaire, intensification, heures supplémentaires —, calé sur l'ordre de grandeur des 35 heures ; salaires mensuels maintenus)",
        "limites": "Pas d'aides publiques d'accompagnement ; heures supplémentaires, temps partiel et négociations de branche non modélisés ; effet sur la fonction publique par embauches compensatrices."},
    "droits_douane": {
        "libelle": "Droits de douane sur les importations hors Union européenne",
        "parametres": {"taux": "droit additionnel (ex. 0.1)", "riposte": "riposte symétrique des partenaires (booléen)", "debut": "année"},
        "modules": ["M5", "M8"], "preuve": "D (part hors UE des importations 45 %, répercussion 80 %, recette nette pour la France 38 %, élasticité des exportations 0,8)",
        "limites": "Relève de la compétence de l'Union européenne ; pas de détournement de commerce ni de change ; riposte stylisée."},
    "tva_reduite": {
        "libelle": "Taux réduits de TVA (5,5 % et 10 %)",
        "parametres": {"points": "variation des deux taux (points)", "debut": "année"},
        "modules": ["M8"], "preuve": "B (rendement : 5 Md€ par point), D (répercussion 80 %, répartition)",
        "limites": "Les deux taux varient ensemble ; répartition par décile approchée."},
    "logements_sociaux": {
        "libelle": "Construction de logements sociaux supplémentaires",
        "parametres": {"milliers": "logements par an", "debut": "année"},
        "modules": ["M8"], "preuve": "B (effet de demande), D (coût 170 k€ par logement, subvention publique 25 %)",
        "limites": "Effets sur les loyers, la mobilité et le pouvoir d'achat des locataires non modélisés."},
})

# Curseurs de l'interface : (clé, groupe, libellé, unité, min, max, pas, valeur actuelle, points précalculés, mesure)
GROUPES = ["Dépenses publiques", "Impôts des ménages", "Impôts sur le capital et le patrimoine", "Entreprises et travail",
           "Prestations", "Retraites", "Environnement et hypothèses"]


def _m(t, **p):
    return {"type": t, "parametres": p}


CURSEURS = [
    # Dépenses publiques
    ("emploi_public", 0, "Emplois publics", "milliers", -200, 200, 10, 0, [-100, 100], lambda v: _m("emploi_public", milliers=v)),
    ("point_indice", 0, "Point d'indice des fonctionnaires", "%", -3, 10, 0.5, 0, [5], lambda v: _m("point_indice", hausse=v / 100)),
    ("sante", 0, "Dépenses de santé", "Md€/an", -20, 30, 1, 0, [10], lambda v: _m("depense_fonction", fonction="santé", md=v)),
    ("education", 0, "Dépenses d'éducation", "Md€/an", -20, 30, 1, 0, [10], lambda v: _m("depense_fonction", fonction="éducation", md=v)),
    ("defense", 0, "Dépenses de défense", "Md€/an", -10, 40, 1, 0, [10], lambda v: _m("depense_fonction", fonction="défense", md=v)),
    ("autres_depenses", 0, "Autres dépenses de fonctionnement", "Md€/an", -60, 30, 1, 0, [-20, 20], lambda v: _m("depense_fonction", fonction="autres", md=v)),
    ("investissement_public", 0, "Investissement public", "Md€/an", -20, 50, 1, 0, [20], lambda v: _m("investissement_public", md=v)),
    # Impôts des ménages
    ("ir_t1", 1, "Impôt sur le revenu : taux de la 1re tranche", "%", 0, 20, 0.5, 11, [9, 13], lambda v: _m("bareme_ir", taux={1: v / 100})),
    ("ir_t2", 1, "Impôt sur le revenu : taux de la 2e tranche", "%", 15, 40, 0.5, 30, [25, 35], lambda v: _m("bareme_ir", taux={2: v / 100})),
    ("ir_t3", 1, "Impôt sur le revenu : taux de la 3e tranche", "%", 30, 55, 0.5, 41, [36, 46], lambda v: _m("bareme_ir", taux={3: v / 100})),
    ("ir_t4", 1, "Impôt sur le revenu : taux de la tranche supérieure", "%", 35, 70, 0.5, 45, [40, 55], lambda v: _m("bareme_ir", taux={4: v / 100})),
    ("ir_seuils", 1, "Impôt sur le revenu : revalorisation des seuils", "%", -5, 5, 0.5, 0, [-3, 3],
     lambda v: _m("bareme_ir", seuils_facteur=1 + v / 100, decote_facteur=1 + v / 100, plafond_qf_facteur=1 + v / 100)),
    ("csg_activite", 1, "CSG sur les revenus d'activité", "points", -3, 3, 0.1, 0, [-1, 1], lambda v: _m("csg", activite_points=v, retraite_points=0.0)),
    ("csg_retraite", 1, "CSG sur les pensions (taux plein)", "points", -3, 3, 0.1, 0, [-1, 1], lambda v: _m("csg", activite_points=0.0, retraite_points=v)),
    ("tva", 1, "Taux normal de TVA", "points", -5, 5, 0.5, 0, [-2, 2], lambda v: _m("tva", points=v)),
    # Capital et patrimoine
    ("pfu", 2, "Flat tax sur les revenus du capital (part IR)", "points", -5, 15, 0.5, 0, [-4, 5], lambda v: _m("pfu", points=v)),
    ("isf", 2, "Impôt sur la fortune (taux moyen, remplace l'IFI)", "%", 0, 2, 0.05, 0, [0.5, 1.0], lambda v: _m("isf", taux_moyen=v)),
    ("successions", 2, "Droits de succession", "%", -50, 100, 5, 0, [-30, 30], lambda v: _m("successions", variation=v / 100)),
    ("taux_is", 2, "Taux de l'impôt sur les sociétés", "%", 15, 40, 0.5, 25.8, [20, 30, 33.3], lambda v: _m("taux_is", taux=v)),
    # Entreprises et travail
    ("cotisations_employeurs", 3, "Cotisations patronales", "Md€/an", -30, 30, 1, 0, [-15, 15], lambda v: _m("cotisations_employeurs", md=v)),
    ("smic", 3, "Coup de pouce au SMIC", "%", 0, 20, 0.5, 0, [5, 10], lambda v: _m("smic", hausse=v / 100)),
    ("salaires", 3, "Hausse générale des salaires (ponctuelle)", "%", -2, 10, 0.5, 0, [-2, 2, 5], lambda v: _m("salaires", hausse=v / 100)),
    ("reindustrialisation", 3, "Objectif de relocalisation industrielle", "% des importations", 0, 30, 1, 0, [5, 10, 20],
     lambda v: _m("reindustrialisation", baisse_parts_importees=v / 100, duree=5, surcout=0.10)),
    # Prestations
    ("rsa", 4, "RSA (montant forfaitaire)", "%", -20, 50, 1, 0, [-10, 10, 25], lambda v: _m("rsa", facteur=1 + v / 100)),
    ("prime_activite", 4, "Prime d'activité", "%", -20, 50, 1, 0, [-10, 10, 25], lambda v: _m("prime_activite", facteur=1 + v / 100)),
    ("allocations_familiales", 4, "Allocations familiales (BMAF)", "%", -20, 50, 1, 0, [-10, 10, 25], lambda v: _m("allocations_familiales", facteur=1 + v / 100)),
    ("aides_logement", 4, "Aides au logement", "%", -20, 30, 1, 0, [-10, 10], lambda v: _m("aides_logement", facteur=1 + v / 100)),
    ("minimum_vieillesse", 4, "Minimum vieillesse (ASPA)", "%", -10, 50, 1, 0, [10, 25], lambda v: _m("minimum_vieillesse", hausse=v / 100)),
    ("assurance_chomage", 4, "Allocations chômage", "%", -30, 20, 1, 0, [-10, 10], lambda v: _m("assurance_chomage", variation=v / 100)),
    ("transferts_menages", 4, "Transferts non ciblés aux ménages", "pt de PIB", -1, 1, 0.1, 0, [-1, 1], lambda v: _m("transferts_menages", points_pib=v)),
    # Retraites
    ("age_legal", 5, "Âge légal de départ (cible)", "ans", 60, 67, 1, 64, [60, 62, 65, 66], lambda v: _m("age_legal", age=v, mode="progressif")),
    ("age_legal_immediat", 5, "Âge légal : retour immédiat (sans transition)", "ans", 60, 64, 1, 64, [60, 62], lambda v: _m("age_legal", age=v, mode="immediat")),
    ("indexation_pensions", 5, "Indexation des pensions (écart à l'inflation, 5 ans)", "pt/an", -2, 2, 0.1, 0, [-1, 1],
     lambda v: _m("indexation_pensions", points=v, duree=5)),
    # Environnement et hypothèses
    ("temps_travail", 3, "Durée légale du travail", "h/semaine", 32, 39, 0.5, 35, [32, 37], lambda v: _m("temps_travail", heures=v, montee=2)),
    ("droits_douane", 3, "Droits de douane hors UE (avec riposte)", "%", 0, 30, 1, 0, [10, 20], lambda v: _m("droits_douane", taux=v / 100, riposte=True)),
    ("tva_reduite", 1, "Taux réduits de TVA", "points", -3, 5, 0.5, 0, [-2, 2], lambda v: _m("tva_reduite", points=v)),
    ("logements_sociaux", 0, "Logements sociaux supplémentaires", "milliers/an", 0, 150, 5, 0, [50], lambda v: _m("logements_sociaux", milliers=v)),
    ("taxe_carbone", 6, "Taxe carbone (hausse)", "€/t CO2", -45, 150, 5, 0, [50, 100], lambda v: _m("taxe_carbone", euros_tonne=v)),
    ("energie_import", 6, "Prix de l'énergie importée (hypothèse)", "%", -30, 60, 5, 0, [-20, 20, 50], lambda v: _m("energie_import", hausse=v / 100)),
]
CURSEURS = [dict(zip(("cle", "groupe", "libelle", "unite", "min", "max", "pas", "actuel", "points", "mesure"), c)) for c in CURSEURS]
for c in CURSEURS:
    c["groupe"] = GROUPES[c["groupe"]]
    c["type"] = c["mesure"](c["points"][0])["type"]

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
