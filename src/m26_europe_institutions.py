"""M26 — Contraintes européennes et risques institutionnels (phase 6).

Objet : pour chaque mesure d'un programme, qualifier sa compatibilité avec le droit de l'Union, la réponse
institutionnelle graduée qu'elle peut déclencher et la traduction macroéconomique de cette réponse dans le modèle
(délais d'application, sanctions financières comptées en dépense publique, prime de risque souveraine via M24,
variantes d'incertitude). Il ne s'agit pas d'un modèle de l'économie européenne : le reste de la zone euro reste
décrit par M11/M24 (taux directeur, Bund, inflation et activité de la zone).

Statut des éléments (convention du projet) :
  [D] règle de droit ou donnée publiée (source citée dans REGLES) ;
  [E] paramètre estimé dans le projet (M24 : prime souveraine) ;
  [H] hypothèse de scénario, documentée et modifiable, jamais estimée ici.

Le module produit des *variantes* : la variante « conforme » (aucune réponse institutionnelle) est la référence de
comparaison ; les variantes « contentieux » et « tension » ne sont pas des prévisions mais des bornes de risque.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------------------------------------------
# Règles de droit de l'Union utilisées [D]
# ---------------------------------------------------------------------------------------------------------------
REGLES = {
    "PDE": {
        "intitule": "Procédure concernant les déficits excessifs (art. 126 TFUE ; règlement (CE) 1467/97 modifié par le "
                    "règlement (UE) 2024/1264, en vigueur depuis le 30 avril 2024)",
        "contenu": "Délai de six mois au plus pour une action suivie d'effets après la recommandation du Conseil ; "
                   "amende pouvant atteindre 0,05 % du PIB de l'année précédente par semestre, payée tous les six mois "
                   "jusqu'à ce que le Conseil constate une action suivie d'effets.",
        "parametres": {"amende_semestrielle_pib": 0.0005, "delai_action_mois": 6},
        "sources": ["https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1784571",
                    "https://oeil.europarl.europa.eu/oeil/fr/document-summary?id=1784571"],
    },
    "VOLET_PREVENTIF": {
        "intitule": "Volet préventif réformé : règlement (UE) 2024/1263 (trajectoire de dépenses nettes du plan "
                    "budgétaire et structurel à moyen terme)",
        "contenu": "Le non-respect de la trajectoire alimente le compte de contrôle ; la PDE fondée sur la dette peut être "
                   "ouverte si les écarts dépassent 0,3 point de PIB par an ou 0,6 point cumulé.",
        "parametres": {"ecart_annuel_pib": 0.3, "ecart_cumule_pib": 0.6},
        "sources": ["https://oeil.europarl.europa.eu/oeil/fr/procedure-document-summary/pdf?id=1770778",
                    "https://www.assemblee-nationale.fr/dyn/17/eurodoc/l17e20048_document-europeen-art88-4"],
    },
    "TVA_TAUX": {
        "intitule": "Directive 2006/112/CE modifiée par la directive (UE) 2022/542 (taux de TVA)",
        "contenu": "Deux taux réduits d'au moins 5 % au plus, applicables à 24 points au plus de l'annexe III ; taux "
                   "inférieurs à 5 % ou nuls limités à sept points ; fin des taux réduits sur les combustibles fossiles "
                   "au 1er janvier 2030. Les carburants routiers ne figurent pas à l'annexe III.",
        "parametres": {"taux_reduit_minimum": 5.0, "fin_fossiles": 2030},
        "sources": ["https://eur-lex.europa.eu/eli/dir/2022/542/oj",
                    "https://sovos.com/fr/blog/tva/mise-a-jour-adoption-des-taux-reduits-de-tva-de-lunion-europeenne/",
                    "https://cms.law/en/fra/news-information/tva-un-nouvel-encadrement-pour-les-taux-reduits"],
    },
    "POLITIQUE_COMMERCIALE": {
        "intitule": "Politique commerciale commune, compétence exclusive de l'Union (art. 3 et 207 TFUE)",
        "contenu": "Les droits de douane sont fixés par l'Union ; un État membre ne peut pas instaurer seul de droits de "
                   "douane sur les importations extra-UE ni sur les échanges intra-UE (art. 30 TFUE).",
        "parametres": {},
        "sources": ["TFUE, art. 3, 30 et 207 (texte des traités)"],
    },
    "CAPITAUX": {
        "intitule": "Libre circulation des capitaux (art. 63 TFUE) ; mesures de sauvegarde (art. 65-66 TFUE)",
        "contenu": "Restrictions interdites entre États membres et avec les pays tiers ; sauvegarde vis-à-vis des pays "
                   "tiers possible par le Conseil pour six mois au plus, en circonstances exceptionnelles.",
        "parametres": {},
        "sources": ["TFUE, art. 63, 65 et 66 (texte des traités)"],
    },
    "AIDES_ETAT": {
        "intitule": "Aides d'État (art. 107-108 TFUE)",
        "contenu": "Les mesures générales (baisse uniforme d'un impôt) ne sont pas des aides d'État ; les mesures "
                   "sélectives doivent être notifiées et autorisées (régimes d'exemption, encadrements).",
        "parametres": {},
        "sources": ["TFUE, art. 107 et 108 (texte des traités)"],
    },
    "NON_DISCRIMINATION": {
        "intitule": "Non-discrimination en raison de la nationalité (art. 18 et 45 TFUE) ; directive 2014/24/UE "
                    "(marchés publics) ; règlement (CE) 883/2004 (coordination de la sécurité sociale)",
        "contenu": "Une préférence fondée sur la nationalité dans l'emploi, les prestations ou les marchés publics est "
                   "incompatible pour les ressortissants de l'Union ; à l'égard des pays tiers, la compatibilité dépend "
                   "des directives sectorielles et de la Constitution (non instruit ici).",
        "parametres": {},
        "sources": ["TFUE, art. 18 et 45 (texte des traités)"],
    },
    "RESSOURCES_PROPRES": {
        "intitule": "Décision relative au système des ressources propres (art. 311 TFUE) et cadre financier pluriannuel",
        "contenu": "La contribution nationale résulte de la décision ressources propres adoptée à l'unanimité ; une "
                   "réduction unilatérale est un manquement (intérêts de retard, recours en manquement).",
        "parametres": {},
        "sources": ["TFUE, art. 311 (texte des traités)"],
    },
    "MANQUEMENT": {
        "intitule": "Recours en manquement (art. 258 et 260 TFUE) ; communication de la Commission sur les sanctions",
        "contenu": "Sanctions après un second arrêt : somme forfaitaire et astreinte ; pour la France, facteur n = 4,45, "
                   "somme forfaitaire minimale 12,46 M€ et astreinte forfaitaire de base 3 000 € par jour, multipliée "
                   "par les coefficients de gravité, de durée et par n.",
        "parametres": {"somme_forfaitaire_min_M€": 12.46, "astreinte_base_jour_€": 3000.0, "facteur_n": 4.45},
        "sources": ["https://www.economie.gouv.fr/node/3219467", "https://eur-lex.europa.eu/eli/C/2025/1481/oj"],
    },
}

# ---------------------------------------------------------------------------------------------------------------
# Échelle des réponses institutionnelles
# ---------------------------------------------------------------------------------------------------------------
NIVEAUX = {
    0: "compatible : compétence nationale, aucune procédure attendue",
    1: "aménagement : compatible sous conditions (notification, rédaction, calendrier) ; risque de report",
    2: "contentieux : procédure en manquement probable ; sanctions faibles à l'échelle macroéconomique, report ou "
       "retrait de la mesure possible",
    3: "budgétaire : effet sur la trajectoire de dépenses nettes et la PDE ; amendes de la PDE possibles",
    4: "rupture : incompatibilité avec les traités sans voie juridique interne ; modélisation hors champ (variante "
       "« non appliquée » seulement)",
}


@dataclass
class Qualification:
    """Qualification d'un type de mesure au regard du droit de l'Union."""
    niveau: int
    regles: tuple
    conformite: str                    # ce que la mesure devient si elle est mise en conformité
    delai_contentieux: int = 0         # années de report typique dans la variante contentieuse [H]
    probabilite_retrait: float = 0.0   # part de la mesure retirée dans la variante contentieuse [H]
    commentaire: str = ""


# Qualification par curseur du simulateur (programme traduit) et par mesure hors curseurs (corpus).
# Les délais et parts retirées sont des hypothèses de scénario [H] : ordre de grandeur d'une procédure en manquement
# (mise en demeure, avis motivé, arrêt) de plusieurs années ; ils ne sont pas estimés.
QUALIFICATIONS = {
    # --- curseurs du simulateur
    "droits_douane": Qualification(4, ("POLITIQUE_COMMERCIALE",), "relèvement négocié du tarif extérieur commun ou "
                                   "mesures de défense commerciale de l'Union (antidumping, sauvegarde)",
                                   commentaire="Le curseur reste simulable comme hypothèse de politique commerciale "
                                               "européenne, pas comme mesure nationale."),
    "tva_reduite": Qualification(1, ("TVA_TAUX",), "taux réduit ≥ 5 % sur les biens de l'annexe III ; énergie fossile "
                                 "exclue à partir de 2030", delai_contentieux=0, probabilite_retrait=0.0),
    "tva": Qualification(0, ("TVA_TAUX",), "taux normal ≥ 15 % (directive 2006/112/CE, art. 97)"),
    "taxe_carbone": Qualification(0, (), "accises nationales au-dessus des minima de la directive 2003/96/CE"),
    "taux_is": Qualification(0, (), "taux effectif minimal de 15 % pour les grands groupes (directive (UE) 2022/2523)"),
    "impots_production": Qualification(0, ("AIDES_ETAT",), "baisse générale : pas d'aide d'État"),
    "cotisations_employeurs": Qualification(0, ("AIDES_ETAT",), "allègements généraux : pas d'aide d'État ; ciblage "
                                            "sectoriel à notifier"),
    "reindustrialisation": Qualification(1, ("AIDES_ETAT",), "aides sélectives notifiées (encadrements, PIIEC)",
                                         delai_contentieux=1, probabilite_retrait=0.0),
    "recherche": Qualification(0, ("AIDES_ETAT",), "régime général d'exemption par catégorie (R&D)"),
    "recettes_neutres": Qualification(0, (), "dépend du contenu : voir les mesures du corpus"),
    **{k: Qualification(0, (), "compétence nationale") for k in (
        "emploi_public", "point_indice", "sante", "education", "defense", "autres_depenses", "investissement_public",
        "formation", "ir_t1", "ir_t2", "ir_t3", "ir_t4", "ir_seuils", "csg_activite", "csg_retraite", "pfu", "isf",
        "successions", "smic", "salaires", "rsa", "prime_activite", "allocations_familiales", "aides_logement",
        "minimum_vieillesse", "assurance_chomage", "transferts_menages", "age_legal", "age_legal_immediat",
        "indexation_pensions", "temps_travail", "logements_sociaux", "energie_import")},
    # --- mesures du corpus sans curseur dédié
    "tva_energie_carburants": Qualification(2, ("TVA_TAUX",), "5,5 % sur électricité et gaz réseau (annexe III) ; "
                                            "carburants : baisse d'accise à la place de la TVA ; gaz fossile : fin du "
                                            "taux réduit en 2030", delai_contentieux=2, probabilite_retrait=0.5,
                                            commentaire="Part retirée = part des carburants dans l'assiette, à "
                                                        "renseigner par la mesure (hypothèse par défaut 0,5)."),
    "contribution_ue_reduite": Qualification(2, ("RESSOURCES_PROPRES", "MANQUEMENT"), "renégociation du prochain "
                                             "cadre financier (unanimité)", delai_contentieux=2,
                                             probabilite_retrait=1.0,
                                             commentaire="Variante contentieuse : l'économie n'est pas réalisée et les "
                                                         "sommes restent dues."),
    "preference_nationale": Qualification(4, ("NON_DISCRIMINATION",), "critères non fondés sur la nationalité "
                                          "(résidence, durée de cotisation) dans les limites du droit de l'Union",
                                          commentaire="Effet macroéconomique non chiffré par les programmes."),
    "controle_capitaux": Qualification(4, ("CAPITAUX",), "mesures prudentielles ou fiscales non discriminatoires"),
    "taxe_transactions_financieres": Qualification(0, (), "taxe nationale existante (TTF française) ; élargissement "
                                                   "possible"),
    "taxe_multinationales": Qualification(1, ("AIDES_ETAT",), "conformité aux conventions fiscales et au pilier 2",
                                          delai_contentieux=1, probabilite_retrait=0.0),
    "blocage_prix_carburant": Qualification(1, ("AIDES_ETAT",), "remise générale à la pompe financée par l'État "
                                            "(précédent de 2022) plutôt que prix administré",
                                            delai_contentieux=0),
    "pole_public_bancaire": Qualification(1, ("AIDES_ETAT",), "établissement public soumis aux règles prudentielles "
                                          "et aux règles d'aides d'État (investisseur avisé)", delai_contentieux=1),
    "regle_or_constitutionnelle": Qualification(0, ("VOLET_PREVENTIF",), "compatible et cohérente avec le volet "
                                                "préventif"),
}


@dataclass
class ScenarioInstitutionnel:
    """Variante institutionnelle appliquée à un programme.

    nom : "conforme" (référence de comparaison : mesures mises en conformité, aucune réponse) ;
          "contentieux" (part non conforme des mesures de niveau 1-2 retirée, mesure suspendue pendant le délai de
          contentieux : application reportée ; voir m27_corpus.mesures) ;
          "tension" (contentieux + amendes PDE + choc de prime souveraine).
    """
    nom: str = "conforme"
    pde_active: bool = False           # amendes de la PDE comptées en dépense
    pde_semestres: int = 0             # nombre de semestres d'amende [H]
    pde_taux: float = REGLES["PDE"]["parametres"]["amende_semestrielle_pib"]   # [D] plafond
    choc_ecart_pb: dict = field(default_factory=dict)   # {année: points de base} sur l'écart OAT-Bund [H]
    prime_crise: bool = False          # coefficients de prime souveraine estimés avec la crise 2010-13 [E] (M24)
    debut: int = 2027

    def __post_init__(self):
        assert self.nom in ("conforme", "contentieux", "tension", "personnalise")


SCENARIOS = {
    "conforme": ScenarioInstitutionnel("conforme"),
    "contentieux": ScenarioInstitutionnel("contentieux"),
    # Tension : quatre semestres d'amende PDE au plafond et un écart souverain accru de 50 pb pendant trois ans, puis
    # coefficients de prime de la période de crise. Les 50 pb sont une hypothèse de scénario [H] : ordre de grandeur
    # de la variation de l'écart OAT-Bund lors des épisodes politiques récents, à remplacer par l'utilisateur.
    "tension": ScenarioInstitutionnel("tension", pde_active=True, pde_semestres=4,
                                      choc_ecart_pb={2027: 50, 2028: 50, 2029: 50}, prime_crise=True),
}


def qualifier(mesures: dict) -> list[dict]:
    """mesures : {clé (curseur ou type du corpus): valeur}. Renvoie la table de compatibilité."""
    out = []
    for k, v in mesures.items():
        q = QUALIFICATIONS.get(k)
        if q is None:
            out.append({"mesure": k, "valeur": v, "niveau": None, "reponse": "non qualifiée (à instruire)",
                        "regles": "", "conformite": "", "delai": None, "retrait": None})
            continue
        if isinstance(v, (int, float)) and v == 0:
            continue
        out.append({"mesure": k, "valeur": v, "niveau": q.niveau, "reponse": NIVEAUX[q.niveau],
                    "regles": ", ".join(q.regles), "conformite": q.conformite, "delai": q.delai_contentieux,
                    "retrait": q.probabilite_retrait, "commentaire": q.commentaire})
    return out


def curseurs_sous_scenario(curseurs: dict, scen: ScenarioInstitutionnel) -> tuple[dict, dict]:
    """Applique la variante à des curseurs du simulateur. Renvoie (curseurs modifiés, reports {curseur: années}).

    - conforme : les curseurs de niveau 4 sont annulés (mesure inapplicable nationalement) ;
    - contentieux/tension : niveau 4 annulés ; niveaux 1-2 réduits de la part retirée, et reportés du délai.
    Les reports sont appliqués par `decaler` sur les écarts transférés (M25).
    """
    c, reports = dict(curseurs), {}
    for k, v in curseurs.items():
        q = QUALIFICATIONS.get(k)
        if q is None:
            continue
        if q.niveau == 4:
            c[k] = 0 if not isinstance(v, bool) else False
        elif scen.nom in ("contentieux", "tension") and q.niveau in (1, 2):
            if isinstance(v, (int, float)) and q.probabilite_retrait:
                c[k] = v * (1.0 - q.probabilite_retrait)
            if q.delai_contentieux:
                reports[k] = q.delai_contentieux
    return c, reports


def amendes_pde(scen: ScenarioInstitutionnel) -> dict:
    """Amendes PDE en points de PIB par année : taux semestriel × nombre de semestres de l'année, à partir de
    scen.debut + 1 (délai de six mois pour agir, puis constat). Le PIB de référence de l'amende est celui de l'année
    précédente ; l'écart avec le PIB courant (croissance nominale ≈ 3 %) est négligé (erreur < 0,003 point de PIB).
    [D] plafond ; [H] nombre de semestres."""
    if not scen.pde_active or scen.pde_semestres <= 0:
        return {}
    out, restant, t = {}, scen.pde_semestres, scen.debut + 1
    while restant > 0:
        n = min(2, restant)
        out[t] = scen.pde_taux * n * 100.0
        restant -= n
        t += 1
    return out


def regime_monetaire(scen: ScenarioInstitutionnel, base: dict | None = None) -> dict:
    """Paramètres de RegimeMonetaire (M24) correspondant à la variante. Prime « écart à la référence » activée dès
    qu'une tension est simulée ; coefficients de crise [E] si prime_crise."""
    import m24_monetaire as M24
    d = dict(base or {"type": "bce", "prime": "ecart_reference"})
    if scen.choc_ecart_pb:
        d["chocs_ecart_souverain"] = {a: pb / 100.0 for a, pb in scen.choc_ecart_pb.items()}
        d.setdefault("prime", "ecart_reference")
    if scen.prime_crise:
        p = M24.parametres()
        d["prime_dette"] = p["prime_dette_avec_crise"]
        d["prime_solde"] = p["prime_solde_avec_crise"]
    return d


def appliquer(scen: ScenarioInstitutionnel, mod, ex):
    """Ajoute les amendes PDE aux dépenses publiques (points de PIB, terme de calage « depenses » de M8) : transfert au
    budget de l'Union, sans effet sur la demande intérieure."""
    import pandas as pd
    am = amendes_pde(scen)
    if not am:
        return
    cal = dict(getattr(ex, "calage", None) or {})
    s = pd.Series(am, dtype=float)
    base = cal.get("depenses")
    cal["depenses"] = base.add(s, fill_value=0.0) if isinstance(base, pd.Series) else s
    ex.calage = cal


def programme(scen: ScenarioInstitutionnel, prog=None):
    """Programme M23 composé : programme d'origine puis réponse institutionnelle (amendes)."""
    import m23_regimes as G
    f0 = prog.appliquer if prog is not None and prog.appliquer is not None else (lambda mod, ex: None)

    def f(mod, ex):
        f0(mod, ex)
        appliquer(scen, mod, ex)
    nom = (prog.nom if prog is not None else "aucun") + f"|{scen.nom}"
    return G.Programme(nom, f, (prog.description if prog is not None else "") + f" ; variante institutionnelle {scen.nom}")


def decaler(trad: dict, reports: dict, curseurs_cle: dict | None = None) -> dict:
    """Report global d'un programme traduit (M25) : si une mesure de niveau 1-2 est reportée, l'ensemble des écarts
    exogènes qui lui sont attribuables ne peut pas être isolé dans les écarts agrégés ; on applique donc le report au
    programme traduit séparément pour la mesure concernée (traduction mesure par mesure, voir m27_corpus). Ici :
    décalage de toutes les séries d'écarts de `delai` années (utilisé pour une traduction mono-mesure)."""
    import pandas as pd
    if not reports:
        return trad
    delai = max(reports.values())
    t2 = copy.deepcopy(trad)
    for k, (mode, val) in list(t2["ecarts"].items()):
        neutre = 1.0 if mode == "ratio" else 0.0
        if isinstance(val, (pd.Series, pd.DataFrame)):
            t2["ecarts"][k] = (mode, val.shift(delai, axis=0).fillna(neutre))
        elif mode == "dictionnaire":
            t2["ecarts"][k] = (mode, {kk: s.shift(delai).fillna(0.0) for kk, s in val.items()})
    if t2.get("mesure_menages"):
        mm = t2["mesure_menages"]
        if "debut" in mm and mm["debut"] is not None:
            mm["debut"] = int(mm["debut"]) + delai
    t2["nom"] = f"{trad['nom']}_report{delai}"
    return t2
