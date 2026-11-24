"""M27 — Corpus des programmes présidentiels 2027 et correspondance avec les paramètres du modèle.

Contenu : mesures économiques et sociales de Jean-Luc Mélenchon (LFI), Marine Le Pen (RN) et Édouard Philippe
(Horizons, retenu comme candidat du centre : programme publié en ligne et volet de finances publiques chiffré
globalement, alors que celui de Gabriel Attal n'était connu que par son enveloppe d'économies à la date du corpus).

État du corpus : 24 novembre 2026. Les programmes évoluent (LFI promet un chiffrage complet début 2027 ; É. Philippe
annonce un « volume 2 » en janvier 2027) : le corpus est daté et versionné, chaque mesure renvoie à sa source.

Règles de constitution (aucune donnée fabriquée) :
  - montant : celui annoncé par le candidat ou son parti (« candidat ») ; à défaut, chiffrage d'un tiers cité
    (« tiers ») ; à défaut « aucun » et montant None ;
  - correspondance (canal) : curseur du simulateur et valeur. Quand le curseur n'est pas en Md€, la valeur est obtenue
    en inversant le rendement statique du simulateur (constantes de simulateur/executer.py) à partir du montant
    annoncé : on simule ainsi « la mesure telle que chiffrée par le candidat », le modèle appliquant ensuite ses propres
    comportements (érosion d'assiette, bouclage) ;
  - les conventions de correspondance qui ne découlent pas du texte sont des hypothèses [H] explicitées dans `regle` ;
  - quantifiable : "oui" (montant et canal), "partiel" (canal identifié, montant manquant ou périmètre ambigu),
    "non" (mesure institutionnelle, réglementaire ou sans canal dans le modèle).
Aucune appréciation politique : les effets annoncés sont ceux revendiqués par les candidats.
"""
from __future__ import annotations

from dataclasses import dataclass, field

DATE_CORPUS = "2026-11-24"

SOURCES = {
    "LFI_BUDGET": "https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf",
    "LFI_AEC": "https://melenchon2027.fr/?p=24158",
    "LFI_PRESSE": "https://melenchon2027.fr/wp-content/uploads/2026/11/DOSSIER-DE-PRESSE_0611_PROGRAMME_ST.pdf",
    "LFI_LCP_BUDGET": "https://lcp.fr/actualites/contre-budget-lfi-propose-1064-milliards-d-euros-de-recettes-supplementaires-et-817",
    "LFI_EPARGNE": "https://lessentieldeleco.fr/9362-melenchon-epargne/",
    "RN_PS_BUDGET": "https://www.publicsenat.fr/actualites/politique/140-milliards-deuros-deconomies-dici-2032-leffort-radical-propose-par-marine-le-pen-pour-redresser-les-f",
    "RN_LCP_JEUNES": "https://lcp.fr/actualites/permis-de-conduire-gratuit-exoneration-d-impot-jusqu-a-30-ans-comment-le-rn-veut",
    "RN_MONEYVOX": "https://www.moneyvox.fr/impot/actualites/110673/140-milliards-economies-ce-quil-faut-retenir-de-intervention-de-marine-le-pen",
    "RN_RETRAITES_PS": "https://www.publicsenat.fr/actualites/politique/presidentielle-2027-que-contient-la-reforme-des-retraites-presentee-par-marine-le-pen",
    "RN_RETRAITES_SUD": "https://www.sudradio.fr/sud-radio/age-de-depart-cotisation-et-capitalisation-les-propositions-du-rn-pour-reformer-les-retraites",
    "RN_RETRAITES_BRUT": "https://www.brut.media/fr/articles/le-pen-affirme-que-sa-reforme-des-retraites-sera-engagee-des-son-arrivee-au-pouvoir-et-sera-appliquee-au-1er-janvier-2028",
    "RN_ENERGIE": "https://www.les-energies-renouvelables.eu/article/actualites/energies/baisse-de-la-tva-arret-du-photovoltaique-ce-que-le-programme-energie-du-rn-changerait-pour-les-menages-2302/",
    "RN_VOTONS": "https://votons-2027.fr/candidats/le-pen/programme",
    "MONTAIGNE_TVA_2022": "https://www.institutmontaigne.org/presidentielle-2022/marine-le-pen/baisser-la-tva-de-20-a-55-pour-les-carburants-lelectricite-le-gaz-et-le-fioul-domestique",
    "EP_COMPTES": "https://www.edouardphilippe.fr/programme/comptes-publics",
    "EP_PS_VOL1": "https://www.publicsenat.fr/actualites/politique/capitalisation-suppression-de-250-000-postes-de-fonctionnaires-autonomie-des-ecoles-fin-des-35-heures-aides-pour-les-familles-edouard-philippe-presente-son-projet-massif-et",
    "EP_EURONEWS": "https://fr.euronews.com/2026/10/09/presidentielle-2027-edouard-philippe-mise-sur-le-travail-et-la-reduction-des-depenses-publ",
    "EP_DEAL": "https://www.publicsenat.fr/actualites/economie/entreprises-un-deal-a-250-milliards-deuros-sur-un-quinquennat-que-represente-la-proposition-dedouard-philippe",
    "SMIC_2026": "https://www.info.gouv.fr/public/index.php/actualite/le-smic-revalorise-le-1er-juin-2026",
}

# Constantes de conversion (reprises du simulateur ; voir simulateur/executer.py et catalogue.py)
RENDEMENT_POINT_PFU = 600.0          # M€ par point
ASSIETTE_ISF, RENDEMENT_IFI = 930_000.0, 2_200.0
RENDEMENT_SUCCESSIONS = 18_000.0
RENDEMENT_POINT_TVA = 8_200.0
DEPENSE_ASSURANCE_CHOMAGE = 40_000.0
SMIC_NET_JUIN_2026 = 1477.93         # € (source SMIC_2026)


@dataclass
class Mesure:
    id: str
    candidat: str
    theme: str
    intitule: str
    montant: float | None = None        # Md€ par an (signe du point de vue des finances publiques : + recette/économie)
    annee: int | None = None             # année de référence du montant
    chiffrage: str = "aucun"             # "candidat" | "tiers" | "aucun"
    calendrier: str = ""
    beneficiaires: str = ""              # ménages ou agents concernés (tels que décrits)
    effets_annonces: str = ""            # effets revendiqués par le candidat
    sources: tuple = ()
    canal: tuple = ()                    # ((curseur, valeur), ...) correspondance centrale
    regle: str = ""                      # règle de conversion et hypothèses [H]
    quantifiable: str = "non"
    ue: str | None = None                # clé de m26_europe_institutions.QUALIFICATIONS
    debut: int = 2027
    regime: str | None = None            # élément de régime (règle budgétaire) plutôt que mesure
    part_ue: float | None = 1.0          # part de la mesure touchée par l'incompatibilité européenne (None : indéterminée,
    #                                      mesure conservée et risque seulement signalé)


def _pfu(md): return md * 1e3 / RENDEMENT_POINT_PFU
def _isf(md): return (md * 1e3 + RENDEMENT_IFI) / ASSIETTE_ISF * 100
def _succ(md): return md * 1e3 / RENDEMENT_SUCCESSIONS * 100
def _tva(md): return -md * 1e3 / RENDEMENT_POINT_TVA
def _ac(md): return md * 1e3 / DEPENSE_ASSURANCE_CHOMAGE * 100


M, L, R, P = [], "melenchon", "le_pen", "philippe"

# ================================================================================================ Jean-Luc Mélenchon
# Document budgétaire du 14 octobre 2026 (année 2027, « budget rectificatif ») : 106,4 Md€ de recettes, 81,7 Md€ de
# dépenses ; ce n'est pas un chiffrage complet de L'Avenir en commun (1 069 mesures, publié le 6 novembre 2026).
B = ("LFI_BUDGET", "LFI_LCP_BUDGET")
M += [
    Mesure("L01", L, "fiscalité du capital", "Suppression du prélèvement forfaitaire unique (flat tax)", 9.0, 2027, "candidat",
           "2027", "détenteurs de revenus du capital", "", B, (("pfu", _pfu(9.0)),),
           "Points de PFU = montant / 0,6 Md€ par point (assiette 60 Md€).", "oui", "pfu"),
    Mesure("L02", L, "patrimoine", "Rétablissement d'un impôt sur la fortune renforcé", 10.0, 2027, "candidat", "2027",
           "patrimoines nets taxables", "", B, (("isf", _isf(10.0)),),
           "Taux moyen = (montant + rendement de l'IFI remplacé) / assiette ISF 930 Md€.", "oui", "isf"),
    Mesure("L03", L, "patrimoine", "Taxe Zucman (patrimoines supérieurs à 100 M€)", 15.0, 2027, "candidat", "2027",
           "très grands patrimoines", "", B, (("recettes_neutres", 15.0),),
           "[H] Assiette (> 100 M€) distincte de celle de l'ISF du modèle : recette sans effet de demande (propension "
           "à consommer quasi nulle) ; l'érosion d'assiette n'est pas représentée (le montant annoncé est une borne "
           "haute). Variante : canal isf (érosion M13).", "partiel", None),
    Mesure("L04", L, "patrimoine", "Réforme des droits de succession", 20.0, 2027, "candidat", "la première année",
           "héritiers", "", B, (("successions", _succ(20.0)),),
           "Variation du rendement = montant / 18 Md€ (au-delà de la borne de l'interface).", "oui", "successions"),
    Mesure("L05", L, "impôt sur le revenu", "Impôt sur le revenu à 14 tranches", None, None, "aucun", "au cours du mandat",
           "contribuables", "", B, (), "Barème non publié : canal ir_t1..ir_t4 identifié, paramètres manquants.",
           "partiel", "ir_t4"),
    Mesure("L06", L, "entreprises", "Rétablissement de la CVAE sur les plus grandes entreprises", 3.0, 2027, "candidat",
           "2027", "grandes entreprises", "", B, (("impots_production", 3.0),), "Md€ directs.", "oui", "impots_production"),
    Mesure("L07", L, "entreprises", "Réforme de l'impôt sur les sociétés", 3.0, 2027, "candidat", "2027", "sociétés", "",
           B, (("taux_is", ("is_md", 3.0)),), "Paramètres non publiés : taux_is calé sur 3 Md€ par le rendement de référence "
           "de l'IS du modèle (fonction conversion_is).", "oui", "taux_is"),
    Mesure("L08", L, "entreprises", "Taxe universelle sur les multinationales", 5.0, 2027, "candidat", "la première année",
           "groupes multinationaux", "", B, (("recettes_neutres", 5.0),),
           "[H] Recette sans effet de demande intérieure (bénéfices en grande partie distribués aux non-résidents).",
           "partiel", "taxe_multinationales"),
    Mesure("L09", L, "entreprises", "Renforcement de la taxe sur les services numériques (GAFAM)", 3.9, 2027, "candidat",
           "2027", "grandes entreprises du numérique", "", B, (("recettes_neutres", 3.9),), "[H] idem L08.", "partiel",
           "recettes_neutres"),
    Mesure("L10", L, "entreprises", "Taxe sur les superprofits", 5.0, 2027, "candidat", "2027", "entreprises", "", B,
           (("recettes_neutres", 5.0),), "[H] Prélèvement exceptionnel sur profits.", "partiel", "recettes_neutres"),
    Mesure("L11", L, "niches", "Rabot et suppression des niches fiscales et sociales « les plus injustes »", 22.0, 2027,
           "candidat", "2027", "non précisé", "", B, (("transferts_menages", ("md", -11.0)), ("cotisations_employeurs", 11.0)),
           "[H] Composition non publiée : moitié ménages (baisse de revenu disponible), moitié entreprises (hausse du "
           "coût du travail). Variante : recettes_neutres.", "partiel", "recettes_neutres"),
    Mesure("L12", L, "entreprises", "Fin des exonérations de cotisations au-dessus de 2 SMIC", None, None, "aucun", "",
           "employeurs", "", B, (), "Canal cotisations_employeurs ; montant non publié.", "partiel", "cotisations_employeurs"),
    Mesure("L13", L, "finance", "Taxes sur les transactions financières", 5.0, 2027, "candidat", "2027", "", "", B,
           (("recettes_neutres", 5.0),), "", "partiel", "taxe_transactions_financieres"),
    Mesure("L14", L, "finance", "Taxe sur les rachats d'actions", 2.5, 2027, "candidat", "2027", "", "", B,
           (("recettes_neutres", 2.5),), "", "partiel", "recettes_neutres"),
    Mesure("L15", L, "finance", "Taxe sur les crypto-actifs", 1.0, 2027, "candidat", "2027", "", "", B,
           (("recettes_neutres", 1.0),), "", "partiel", "recettes_neutres"),
    Mesure("L16", L, "fraude", "Lutte contre la fraude fiscale", 2.0, 2027, "candidat", "la première année", "", "", B,
           (("recettes_neutres", 2.0),), "", "partiel", "recettes_neutres"),
    # dépenses (montants négatifs : dégradation du solde)
    Mesure("L20", L, "fonction publique", "Dégel et hausse de 10 % du point d'indice", -17.0, 2027, "candidat", "2027",
           "agents publics", "relance par les revenus", B, (("point_indice", 10.0),), "Point d'indice +10 %.", "oui",
           "point_indice"),
    Mesure("L21", L, "prestations", "Revalorisation de 10 % des pensions, allocations familiales et APL", -8.0, 2027,
           "candidat", "2027", "retraités, familles, locataires", "", B, (("transferts_menages", ("md", 8.0)),),
           "[H] Le montant annoncé (8 Md€) n'est pas compatible avec une revalorisation générale de toutes les "
           "pensions (masse de plusieurs centaines de Md€) : périmètre à préciser ; montant annoncé versé en transferts "
           "non ciblés. Variante : allocations_familiales et aides_logement +10 % (microsimulation).", "partiel", None),
    Mesure("L22", L, "logement", "Logements d'urgence et réquisition de logements vacants", -3.0, 2027, "candidat", "2027",
           "personnes sans logement", "", B, (("autres_depenses", 3.0),), "", "oui", None),
    Mesure("L23", L, "jeunesse", "Garantie d'autonomie pour les jeunes", -9.5, 2027, "candidat", "2027", "jeunes", "", B,
           (("transferts_menages", ("md", 9.5)),), "[H] Transfert non ciblé (pas de mesure jeunes dans M4).", "oui", None),
    Mesure("L24", L, "salaires", "SMIC à 1 700 € net", None, None, "aucun", "", "salariés au SMIC", "", B + ("SMIC_2026",),
           (("smic", (1700 / SMIC_NET_JUIN_2026 - 1) * 100),), "Hausse = 1 700 / 1 477,93 − 1 ≈ 15,0 % (SMIC net au "
           "1er juin 2026).", "oui", "smic"),
    Mesure("L25", L, "énergie", "Blocage du prix des carburants à 1,70 €/l", None, None, "aucun", "", "automobilistes", "",
           B, (), "Coût dépendant du prix de marché : canal energie_import + subvention, non chiffrable sans hypothèse "
           "de prix.", "partiel", "blocage_prix_carburant"),
    Mesure("L26", L, "éducation", "10 000 postes dans l'Éducation nationale", -0.5, 2027, "candidat", "2027", "élèves", "",
           B, (("education", 0.5),), "", "oui", None),
    Mesure("L27", L, "éducation", "Gratuité de la cantine scolaire", -3.6, 2027, "candidat", "2027", "familles", "", B,
           (("education", 3.6),), "[H] Dépense de fonctionnement (transfert en nature).", "oui", None),
    Mesure("L28", L, "éducation", "250 000 places à l'université", -3.5, 2027, "candidat", "2027", "étudiants", "", B,
           (("education", 3.5),), "", "oui", None),
    Mesure("L29", L, "santé", "Hôpital public (+10 000 postes soignants)", -3.0, 2027, "candidat", "2027", "", "", B,
           (("sante", 3.0),), "", "oui", None),
    Mesure("L30", L, "services publics", "Violences sexistes et sexuelles ; violences faites aux enfants", -4.6, 2027,
           "candidat", "2027", "", "", B, (("autres_depenses", 4.6),), "2,6 + 2,0 Md€.", "oui", None),
    Mesure("L31", L, "services publics", "Indexation des budgets 2027 des services supprimés en 2026", -7.0, 2027, "candidat",
           "2027", "", "", B, (("autres_depenses", 7.0),), "", "oui", None),
    Mesure("L32", L, "écologie", "Adaptation au dérèglement climatique", -10.0, 2027, "candidat", "dès 2026", "", "", B,
           (("investissement_public", 10.0),), "", "oui", None),
    Mesure("L33", L, "écologie", "Investissements de planification écologique portés par le pôle public bancaire", None,
           None, "candidat", "par an, hors budget de l'État", "", "", B, (("investissement_hors_apu", 100.0),),
           "100 Md€ par an annoncés hors budget : investissement hors APU (effet de demande sans coût pour le solde "
           "public). [H] Montée en charge non précisée : appliqué dès 2028 ; additionnalité totale (borne haute). "
           "Financement, dette du pôle public et effet d'offre non représentés.", "partiel", "pole_public_bancaire",
           debut=2028),
    Mesure("L34", L, "retraites", "Abrogation de la réforme de 2023 (retour à 62 ans)", -9.0, 2027, "candidat",
           "dès l'année suivant l'élection", "assurés", "", B, (("age_legal_immediat", 62),),
           "Coût calculé par M9 (le montant annoncé sert de contrôle).", "oui", None),
    Mesure("L35", L, "assurance chômage", "Abrogation des réformes de l'assurance chômage", -3.0, 2027, "candidat",
           "dès l'année suivant l'élection", "demandeurs d'emploi", "", B, (("assurance_chomage", _ac(3.0)),),
           "Variation = montant / 40 Md€ de dépense.", "oui", None),
    Mesure("L36", L, "retraites", "Retour à 60 ans avec 40 annuités", None, None, "aucun", "en un mandat", "assurés", "",
           B, (("age_legal", 60),), "Objectif de mandat : variante (non incluse dans le paquet 2027).", "partiel", None,
           debut=2028),
    Mesure("L37", L, "épargne", "Plafond du livret A relevé à 30 000 € ; centralisation portée à 80 % ; livret B",
           None, None, "aucun", "", "épargnants", "", ("LFI_BUDGET", "LFI_EPARGNE"), (),
           "Pas de canal de l'intermédiation financière dans le modèle.", "non", "pole_public_bancaire"),
    Mesure("L38", L, "finance", "Contrôle des capitaux ; fin de la cotation continue", None, None, "aucun", "", "", "",
           ("LFI_EPARGNE",), (), "Mesures de régulation sans canal.", "non", "controle_capitaux"),
    Mesure("L39", L, "finances publiques", "Réduction du déficit de 25 Md€ par an ; stabilisation de la dette en un "
           "quinquennat", None, None, "candidat", "2027-2032", "", "retour de l'activité dès 2028", B, (),
           "Objectif de solde : élément de régime (pas de règle automatique).", "non", None, regime="objectif"),
]

# ================================================================================================ Marine Le Pen
RB = ("RN_PS_BUDGET", "RN_MONEYVOX")
M += [
    Mesure("P01", R, "finances publiques", "140 Md€ d'économies nettes d'ici 2032 ; dette de 121 % (2027) à 112 % (2032) ; "
           "déficit à 3 % en 2030 ; 30 Md€ de baisses d'impôts", 140.0, 2032, "candidat", "2027-2032", "", "", RB, (),
           "Enveloppe agrégée : les mesures détaillées ci-dessous en couvrent une partie.", "non", None, regime="objectif"),
    Mesure("P02", R, "finances publiques", "Règle d'or constitutionnelle par référendum (déficit plafonné au niveau "
           "stabilisant la dette)", None, None, "candidat", "dans les 12 mois", "", "", ("RN_PS_BUDGET",), (),
           "Élément de régime : règle de stabilisation (M23 R1, mode actif).", "non", "regle_or_constitutionnelle",
           regime="R1_actif"),
    Mesure("P03", R, "immigration", "Économies sur le « coût de l'immigration »", 15.0, 2027, "candidat",
           "15 Md€ en 2027, 29 Md€ en année pleine", "", "", ("RN_PS_BUDGET",), (("transferts_menages", ("md", -15.0)),),
           "[H] Composition non publiée : baisse de prestations (transferts). La part fondée sur la nationalité est "
           "incompatible pour les ressortissants de l'Union (M26, niveau 4) ; cette part n'est pas connue.", "partiel",
           "preference_nationale", part_ue=None),
    Mesure("P04", R, "Union européenne", "Baisse de la contribution au budget de l'Union", 9.0, 2027, "candidat", "2027", "",
           "", ("RN_PS_BUDGET",), (("recettes_neutres", 9.0),), "Recette nette sans effet de demande.", "oui",
           "contribution_ue_reduite"),
    Mesure("P05", R, "État", "Réorganisation de l'État (centralisation de la TVA, transferts aux collectivités et à la "
           "Sécurité sociale votés par le Parlement)", 20.7, 2027, "candidat", "dès 2027", "", "", ("RN_PS_BUDGET",),
           (("autres_depenses", -20.7),),
           "[H] Les sources ne disent pas si les économies sur les collectivités (P06) et les agences (P07) sont "
           "incluses : par prudence, P06 et P07 sont traitées comme des composantes de P05 (non additionnées).",
           "partiel", None),
    Mesure("P06", R, "collectivités", "Contribution des collectivités (dont suppression des EPCI et métropoles 0,25 Md€, "
           "effectifs 0,8 Md€)", 8.2, 2027, "candidat", "2027", "", "", ("RN_PS_BUDGET",), (), "Composante de P05 [H].",
           "partiel", None),
    Mesure("P07", R, "État", "Agences de l'État", 3.4, 2027, "candidat", "2027", "", "", ("RN_PS_BUDGET",), (),
           "Composante de P05 [H] ; une commission sénatoriale évaluait ces économies à environ 0,5 Md€.", "partiel", None),
    Mesure("P08", R, "retraites", "Âge légal ramené à 62 ans (60 ans pour les carrières commencées avant 20 ans), 42 "
           "annuités ; pilier de capitalisation obligatoire (socle : Fonds de réserve pour les retraites)", -18.6, 2032,
           "candidat", "application au 1er janvier 2028", "assurés", "réforme « pleinement financée »",
           ("RN_RETRAITES_PS", "RN_RETRAITES_SUD", "RN_RETRAITES_BRUT"), (("age_legal", 62),),
           "Coût brut annoncé 18,6 Md€ en 2032. Carrières longues, durée et pilier de capitalisation non représentés "
           "dans M9 (extension identifiée, doc 26).", "partiel", None, debut=2028),
    Mesure("P09", R, "retraites", "Économies sur les retraites (« corrections de mesures injustes »)", 17.5, 2032, "candidat",
           "à terme", "", "", ("RN_PS_BUDGET", "RN_MONEYVOX"), (),
           "Fourchette 15-20 Md€, mesures non détaillées.", "partiel", None),
    Mesure("P10", R, "énergie", "TVA ramenée de 20 % à 5,5 % sur l'électricité, le gaz, le fioul et les carburants",
           -10.0, 2022, "tiers", "", "consommateurs d'énergie", "baisse des prix de l'énergie",
           ("RN_ENERGIE", "MONTAIGNE_TVA_2022"), (("tva", _tva(10.0)),),
           "Coût : ordre de grandeur de l'Institut Montaigne (2022), aucun montant du candidat dans les sources. [H] "
           "Baisse équivalente du taux normal (le modèle ne distingue pas l'énergie) : la répercussion sur les prix est "
           "répartie sur toute la consommation.", "partiel", "tva_energie_carburants"),
    Mesure("P11", R, "jeunesse", "Exonération d'impôt sur le revenu des moins de 30 ans (jusqu'à 4 SMIC)", -2.0, 2027,
           "candidat", "", "moins de 30 ans", "", ("RN_LCP_JEUNES",), (("transferts_menages", ("md", 2.0)),),
           "[H] Baisse d'impôt traitée en transfert non ciblé.", "oui", None),
    Mesure("P12", R, "jeunesse", "Permis de conduire gratuit (18 ans, casier vierge) ; prime d'activité étudiante", -1.3,
           2027, "candidat", "", "700 000 jeunes par an (permis)", "", ("RN_LCP_JEUNES",),
           (("transferts_menages", ("md", 1.3)),), "0,7 + 0,6 Md€.", "oui", None),
    Mesure("P13", R, "familles", "Part fiscale pleine dès le deuxième enfant", -3.5, 2027, "candidat", "2027", "familles", "",
           ("RN_LCP_JEUNES",), (("transferts_menages", ("md", 3.5)),), "[H] Transfert non ciblé.", "oui", None),
    Mesure("P14", R, "familles", "Dons familiaux défiscalisés ; prêt à taux zéro au troisième enfant ; suppression de la "
           "CVEC", None, None, "aucun", "", "familles, étudiants", "", ("RN_LCP_JEUNES",), (), "", "partiel", None),
    Mesure("P15", R, "entreprises", "Suppression de la CFE et des impôts de production « qui nuisent à la relocalisation »",
           None, None, "aucun", "", "entreprises", "relocalisation", ("RN_VOTONS",), (("impots_production", None),),
           "Montant non publié : canal impots_production.", "partiel", "impots_production"),
    Mesure("P16", R, "préférence nationale", "Priorité nationale (logement, emploi, prestations)", None, None, "aucun", "",
           "", "", ("RN_LCP_JEUNES",), (), "", "non", "preference_nationale"),
]

# ================================================================================================ Édouard Philippe
E = ("EP_COMPTES", "EP_PS_VOL1")
M += [
    Mesure("H01", P, "finances publiques", "Près de 150 Md€ d'économies ; déficit sous 2,5 % du PIB en fin de quinquennat ; "
           "moitié de l'effort sur les dépenses sociales, un quart sur l'État et les collectivités, un quart sur la "
           "croissance", 150.0, 2032, "candidat", "quinquennat", "", "", E, (), "Enveloppe agrégée.", "non", None,
           regime="objectif"),
    Mesure("H02", P, "finances publiques", "Règle d'or constitutionnelle par référendum ; aucun nouvel impôt pendant "
           "cinq ans", None, None, "candidat", "dès le début du quinquennat", "", "", E, (),
           "Élément de régime : trajectoire de rétablissement (M23 R2, mode actif, instruments de dépense).", "non",
           "regle_or_constitutionnelle", regime="R2_actif_depenses"),
    Mesure("H03", P, "fonction publique", "250 000 postes de fonctionnaires en moins (un départ sur trois non remplacé dans "
           "les fonctions de bureau)", None, None, "aucun", "quinquennat", "", "gains de productivité de l'IA", E,
           (("emploi_public", -250),), "Effectif atteint en 5 ans ; coût moyen du simulateur 56 k€ par agent.", "oui", None),
    Mesure("H04", P, "fonction publique", "Hausse de 20 % du salaire des enseignants", None, None, "aucun", "quinquennat",
           "enseignants", "", ("EP_PS_VOL1",), (), "Masse salariale des enseignants non disponible dans le modèle : "
           "canal education (Md€) à chiffrer.", "partiel", None),
    Mesure("H05", P, "retraites", "Âge de départ à 65 ans et 45 annuités ; départ précoce pour un tiers des assurés ; "
           "capitalisation collective", None, None, "aucun", "non précisé", "assurés", "", E + ("EP_EURONEWS",),
           (("age_legal", 65),), "Durée d'assurance, départs précoces et capitalisation non représentés dans M9.",
           "partiel", None, debut=2028),
    Mesure("H06", P, "travail", "Fin des 35 heures ; deux heures supplémentaires hebdomadaires exonérées de cotisations",
           None, None, "aucun", "ordonnances de juillet 2027", "salariés", "≈ 1 000 € par an pour un salarié au SMIC",
           ("EP_PS_VOL1", "EP_EURONEWS"), (("temps_travail", 37),),
           "[H] Durée de référence portée à 37 h (2 h supplémentaires) ; exonération non chiffrée.", "partiel", None),
    Mesure("H07", P, "assurance chômage", "Indemnisation limitée à 12 mois pour les moins de 50 ans", None, None, "aucun",
           "", "demandeurs d'emploi", "", E + ("EP_EURONEWS",), (("assurance_chomage", None),),
           "Le curseur agit sur les montants, pas sur la durée : montant à chiffrer.", "partiel", None),
    Mesure("H08", P, "minima sociaux", "Baisse de 30 % du nombre d'allocataires du RSA (accompagnement, métiers en tension)",
           None, None, "aucun", "", "allocataires du RSA", "le travail paie plus que l'inactivité", E,
           (("rsa", -30),), "[H] Le curseur réduit le montant forfaitaire (−30 %) : approximation budgétaire d'une "
           "baisse des effectifs ; la réponse de participation passe par M15 (gain à l'emploi accru), pas par "
           "l'accompagnement annoncé ; effet distributif différent d'une baisse d'effectifs.", "partiel", None),
    Mesure("H09", P, "santé", "Trois jours de carence pour tous (public et privé)", None, None, "aucun", "", "salariés", "",
           E, (), "Pas de canal des indemnités journalières.", "non", None),
    Mesure("H10", P, "familles", "Allocation de 350 € par mois dès le premier enfant, dégressive ; exonération d'impôt "
           "les trois premières années de l'enfant ; suppression des frais de notaire au premier achat (< 35 ans) ; "
           "prêt à taux zéro famille", None, None, "aucun", "", "familles", "", E + ("EP_EURONEWS",), (),
           "Barèmes non publiés.", "partiel", None),
    Mesure("H11", P, "entreprises", "Baisse de 50 Md€ des impôts de production financée par 50 Md€ de baisse des aides "
           "aux entreprises", 0.0, 2028, "candidat", "dès la première loi de finances, pacte pluriannuel", "entreprises",
           "compétitivité", ("EP_PS_VOL1", "EP_DEAL"), (("impots_production", -25.0), ("cotisations_employeurs", 25.0)),
           "[H] Composition des aides non publiée. Le modèle représente une aide supprimée de deux façons : (a) aide "
           "assimilable à une moindre imposition de la production (subventions, dépenses fiscales) : même canal que les "
           "impôts de production, de signe opposé, donc effet net nul ; (b) allègement de cotisations supprimé : hausse "
           "du coût du travail (cotisations_employeurs). Central : moitié (a), moitié (b), soit impôts de production "
           "−25 Md€ nets et cotisations +25 Md€. Variantes : (a) seul (mesure neutre dans le modèle) ; (b) seul "
           "(impôts de production −50, cotisations +50). Limite : le modèle ne distingue pas les distorsions propres "
           "aux impôts de production de celles des subventions (argument central du candidat). Début : première loi de "
           "finances du quinquennat (2028).", "partiel", "impots_production", debut=2028),
    Mesure("H12", P, "écologie", "Fonds unique d'adaptation au changement climatique", -2.0, 2027, "candidat", "par an", "",
           "", ("EP_EURONEWS",), (("investissement_public", 2.0),), "", "oui", None),
    Mesure("H13", P, "État", "Fusion, suppression ou privatisation d'une trentaine d'agences (dont France Travail)", None,
           None, "aucun", "", "", "", E, (), "", "partiel", None),
    Mesure("H14", P, "énergie", "Huit réacteurs nucléaires supplémentaires ; suppression du ZAN", None, None, "aucun", "",
           "", "", ("EP_PS_VOL1",), (), "", "non", None),
]

MESURES = {m.id: m for m in M}
CANDIDATS = {L: "Jean-Luc Mélenchon (LFI)", R: "Marine Le Pen (RN)", P: "Édouard Philippe (Horizons)"}


TAUX_IS_ACTUEL = 25.8


def conversion_is(reference, md: float, annee: int = 2027) -> float:
    """Taux d'IS (curseur absolu) donnant un rendement statique `md` (Md€) : rendement par point = IS de référence de
    l'année (M€, compte des sociétés) / taux légal actuel."""
    is_ref = float(reference["is_"].get(annee, reference["is_"].iloc[-1]))
    return TAUX_IS_ACTUEL + md * 1e3 / (is_ref / TAUX_IS_ACTUEL)


def curseurs(candidat: str, reference, annee: int = 2027, inclure_variantes=False) -> tuple[dict, list]:
    """Paquet de curseurs du candidat (correspondance centrale) et liste des mesures non représentées.

    reference : trajectoire de référence de l'environnement (M€) ; sert à convertir les transferts exprimés en Md€ en
    points de PIB (curseur transferts_menages) et les rendements d'IS en taux. Les mesures à valeur None (montant à préciser) sont listées, pas simulées."""
    pib = float(reference["pib_nominal"].get(annee)) / 1e3
    out, hors = {}, []
    for m in M:
        if m.candidat != candidat:
            continue
        if m.debut != 2027 and not inclure_variantes and m.id in ("L36",):
            hors.append((m.id, "variante de mandat")); continue
        if not m.canal:
            hors.append((m.id, m.quantifiable)); continue
        for cle, v in m.canal:
            if v is None:
                hors.append((m.id, f"{cle} : montant à préciser")); continue
            if isinstance(v, tuple) and v[0] == "md":
                v = v[1] / pib * 100
            elif isinstance(v, tuple) and v[0] == "is_md":
                v = conversion_is(reference, v[1], annee)
                out[cle] = v; continue
            if cle in ("age_legal", "age_legal_immediat", "temps_travail"):
                out[cle] = v
            else:
                out[cle] = out.get(cle, 0.0) + v
    return out, hors


def _valeur(m: "Mesure", v, reference, annee):
    if isinstance(v, tuple) and v[0] == "md":
        return v[1] / (float(reference["pib_nominal"].get(annee)) / 1e3) * 100
    if isinstance(v, tuple) and v[0] == "is_md":
        return conversion_is(reference, v[1], annee)
    return v


ABSOLUS = ("age_legal", "age_legal_immediat", "temps_travail", "taux_is")
NEUTRES = {"age_legal": 64, "age_legal_immediat": 64, "temps_travail": 35, "taux_is": TAUX_IS_ACTUEL}


def mesures(candidat: str, reference, scenario=None, annee: int = 2027, inclure_variantes=False) -> tuple[list, list]:
    """Liste (curseur, valeur, début, id) du paquet central du candidat, sous une variante institutionnelle de M26
    (None ou "conforme" : mesures de niveau 4 retirées pour leur part non conforme ; "contentieux"/"tension" : en plus,
    mesures de niveau 1-2 réduites de la part retirée et reportées du délai de contentieux). Renvoie aussi la liste des
    mesures non simulées avec le motif."""
    import m26_europe_institutions as U
    sc = U.SCENARIOS[scenario] if isinstance(scenario, str) else scenario
    out, hors = [], []
    for m in M:
        if m.candidat != candidat:
            continue
        if m.id == "L36" and not inclure_variantes:
            hors.append((m.id, "variante de mandat")); continue
        if not m.canal:
            hors.append((m.id, m.quantifiable)); continue
        q = U.QUALIFICATIONS.get(m.ue) if m.ue else None
        facteur, report = 1.0, 0
        if q is not None and q.niveau == 4 and m.part_ue:
            facteur = 1.0 - m.part_ue
        if q is not None and sc is not None and sc.nom in ("contentieux", "tension") and q.niveau in (1, 2):
            facteur *= 1.0 - q.probabilite_retrait * (m.part_ue or 0.0)
            report = q.delai_contentieux
        for cle, v in m.canal:
            if v is None:
                hors.append((m.id, f"{cle} : montant à préciser")); continue
            x = _valeur(m, v, reference, annee)
            if facteur != 1.0:
                x = NEUTRES[cle] + (x - NEUTRES[cle]) * facteur if cle in ABSOLUS else x * facteur
                if facteur == 0.0:
                    hors.append((m.id, "retirée (incompatibilité européenne)")); continue
            out.append((cle, x, m.debut + report, m.id))
    return out, hors


def debuts(candidat: str) -> dict:
    """Première année d'application par curseur (mesures dont le calendrier diffère de 2027)."""
    d = {}
    for m in M:
        if m.candidat == candidat and m.debut != 2027:
            for cle, _ in m.canal:
                d[cle] = m.debut
    return d


def table(candidat: str | None = None):
    import pandas as pd
    rows = [{"id": m.id, "candidat": m.candidat, "theme": m.theme, "intitule": m.intitule, "montant_Md€": m.montant,
             "annee": m.annee, "chiffrage": m.chiffrage, "calendrier": m.calendrier, "beneficiaires": m.beneficiaires,
             "canal": "; ".join(f"{c}={v}" for c, v in m.canal), "quantifiable": m.quantifiable, "ue": m.ue,
             "regime": m.regime, "regle": m.regle, "sources": ", ".join(m.sources)}
            for m in M if candidat in (None, m.candidat)]
    return pd.DataFrame(rows)
