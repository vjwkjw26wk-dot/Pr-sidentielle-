# 24 — Phase 6 : contraintes européennes et risques institutionnels

Module : `src/m26_europe_institutions.py`. Couplage avec le corpus : `src/m27_corpus.mesures(candidat, reference,
scenario)`. Test de simulabilité : `phase6/simulabilite.py`. Pas de modèle de l'économie européenne : le reste de la
zone euro reste décrit par M11 et M24 (taux directeur, Bund, inflation et activité de la zone).

## 1. Démarche

Pour chaque mesure : (1) règle de droit de l'Union concernée [D] ; (2) niveau de réponse institutionnelle ;
(3) forme mise en conformité ; (4) traduction macroéconomique de la réponse (report, retrait partiel, amende comptée
en dépense, prime souveraine). Les paramètres de durée et de retrait sont des **hypothèses de scénario [H]** : le
module produit des variantes encadrantes, pas des prévisions juridiques.

## 2. Règles de droit utilisées

| clé | texte | contenu retenu | sources |
|---|---|---|---|
| `PDE` | Procédure concernant les déficits excessifs (art. 126 TFUE ; règlement (CE) 1467/97 modifié par le règlement (UE) 2024/1264, en vigueur depuis le 30 avril 2024) | Délai de six mois au plus pour une action suivie d'effets après la recommandation du Conseil ; amende pouvant atteindre 0,05 % du PIB de l'année précédente par semestre, payée tous les six mois jusqu'à ce que le Conseil constate une action suivie d'effets. | https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1784571; https://oeil.europarl.europa.eu/oeil/fr/document-summary?id=1784571 |
| `VOLET_PREVENTIF` | Volet préventif réformé : règlement (UE) 2024/1263 (trajectoire de dépenses nettes du plan budgétaire et structurel à moyen terme) | Le non-respect de la trajectoire alimente le compte de contrôle ; la PDE fondée sur la dette peut être ouverte si les écarts dépassent 0,3 point de PIB par an ou 0,6 point cumulé. | https://oeil.europarl.europa.eu/oeil/fr/procedure-document-summary/pdf?id=1770778; https://www.assemblee-nationale.fr/dyn/17/eurodoc/l17e20048_document-europeen-art88-4 |
| `TVA_TAUX` | Directive 2006/112/CE modifiée par la directive (UE) 2022/542 (taux de TVA) | Deux taux réduits d'au moins 5 % au plus, applicables à 24 points au plus de l'annexe III ; taux inférieurs à 5 % ou nuls limités à sept points ; fin des taux réduits sur les combustibles fossiles au 1er janvier 2030. Les carburants routiers ne figurent pas à l'annexe III. | https://eur-lex.europa.eu/eli/dir/2022/542/oj; https://sovos.com/fr/blog/tva/mise-a-jour-adoption-des-taux-reduits-de-tva-de-lunion-europeenne/; https://cms.law/en/fra/news-information/tva-un-nouvel-encadrement-pour-les-taux-reduits |
| `POLITIQUE_COMMERCIALE` | Politique commerciale commune, compétence exclusive de l'Union (art. 3 et 207 TFUE) | Les droits de douane sont fixés par l'Union ; un État membre ne peut pas instaurer seul de droits de douane sur les importations extra-UE ni sur les échanges intra-UE (art. 30 TFUE). | TFUE, art. 3, 30 et 207 (texte des traités) |
| `CAPITAUX` | Libre circulation des capitaux (art. 63 TFUE) ; mesures de sauvegarde (art. 65-66 TFUE) | Restrictions interdites entre États membres et avec les pays tiers ; sauvegarde vis-à-vis des pays tiers possible par le Conseil pour six mois au plus, en circonstances exceptionnelles. | TFUE, art. 63, 65 et 66 (texte des traités) |
| `AIDES_ETAT` | Aides d'État (art. 107-108 TFUE) | Les mesures générales (baisse uniforme d'un impôt) ne sont pas des aides d'État ; les mesures sélectives doivent être notifiées et autorisées (régimes d'exemption, encadrements). | TFUE, art. 107 et 108 (texte des traités) |
| `NON_DISCRIMINATION` | Non-discrimination en raison de la nationalité (art. 18 et 45 TFUE) ; directive 2014/24/UE (marchés publics) ; règlement (CE) 883/2004 (coordination de la sécurité sociale) | Une préférence fondée sur la nationalité dans l'emploi, les prestations ou les marchés publics est incompatible pour les ressortissants de l'Union ; à l'égard des pays tiers, la compatibilité dépend des directives sectorielles et de la Constitution (non instruit ici). | TFUE, art. 18 et 45 (texte des traités) |
| `RESSOURCES_PROPRES` | Décision relative au système des ressources propres (art. 311 TFUE) et cadre financier pluriannuel | La contribution nationale résulte de la décision ressources propres adoptée à l'unanimité ; une réduction unilatérale est un manquement (intérêts de retard, recours en manquement). | TFUE, art. 311 (texte des traités) |
| `MANQUEMENT` | Recours en manquement (art. 258 et 260 TFUE) ; communication de la Commission sur les sanctions | Sanctions après un second arrêt : somme forfaitaire et astreinte ; pour la France, facteur n = 4,45, somme forfaitaire minimale 12,46 M€ et astreinte forfaitaire de base 3 000 € par jour, multipliée par les coefficients de gravité, de durée et par n. | https://www.economie.gouv.fr/node/3219467; https://eur-lex.europa.eu/eli/C/2025/1481/oj |

## 3. Échelle des réponses

| niveau | réponse |
|---|---|
| 0 | compatible : compétence nationale, aucune procédure attendue |
| 1 | aménagement : compatible sous conditions (notification, rédaction, calendrier) ; risque de report |
| 2 | contentieux : procédure en manquement probable ; sanctions faibles à l'échelle macroéconomique, report ou retrait de la mesure possible |
| 3 | budgétaire : effet sur la trajectoire de dépenses nettes et la PDE ; amendes de la PDE possibles |
| 4 | rupture : incompatibilité avec les traités sans voie juridique interne ; modélisation hors champ (variante « non appliquée » seulement) |

## 4. Qualification des mesures (extrait : niveaux ≥ 1 et cas de référence)

| clé | niveau | règles | forme conforme | délai contentieux [H] (années) | part retirée [H] | commentaire |
|---|---|---|---|---|---|---|
| `droits_douane` | 4 | POLITIQUE_COMMERCIALE | relèvement négocié du tarif extérieur commun ou mesures de défense commerciale de l'Union (antidumping, sauvegarde) | 0 | 0.0 | Le curseur reste simulable comme hypothèse de politique commerciale européenne, pas comme mesure nationale. |
| `tva_reduite` | 1 | TVA_TAUX | taux réduit ≥ 5 % sur les biens de l'annexe III ; énergie fossile exclue à partir de 2030 | 0 | 0.0 |  |
| `tva` | 0 | TVA_TAUX | taux normal ≥ 15 % (directive 2006/112/CE, art. 97) | 0 | 0.0 |  |
| `taux_is` | 0 | — | taux effectif minimal de 15 % pour les grands groupes (directive (UE) 2022/2523) | 0 | 0.0 |  |
| `impots_production` | 0 | AIDES_ETAT | baisse générale : pas d'aide d'État | 0 | 0.0 |  |
| `reindustrialisation` | 1 | AIDES_ETAT | aides sélectives notifiées (encadrements, PIIEC) | 1 | 0.0 |  |
| `tva_energie_carburants` | 2 | TVA_TAUX | 5,5 % sur électricité et gaz réseau (annexe III) ; carburants : baisse d'accise à la place de la TVA ; gaz fossile : fin du taux réduit en 2030 | 2 | 0.5 | Part retirée = part des carburants dans l'assiette, à renseigner par la mesure (hypothèse par défaut 0,5). |
| `contribution_ue_reduite` | 2 | RESSOURCES_PROPRES, MANQUEMENT | renégociation du prochain cadre financier (unanimité) | 2 | 1.0 | Variante contentieuse : l'économie n'est pas réalisée et les sommes restent dues. |
| `preference_nationale` | 4 | NON_DISCRIMINATION | critères non fondés sur la nationalité (résidence, durée de cotisation) dans les limites du droit de l'Union | 0 | 0.0 | Effet macroéconomique non chiffré par les programmes. |
| `controle_capitaux` | 4 | CAPITAUX | mesures prudentielles ou fiscales non discriminatoires | 0 | 0.0 |  |
| `taxe_multinationales` | 1 | AIDES_ETAT | conformité aux conventions fiscales et au pilier 2 | 1 | 0.0 |  |
| `blocage_prix_carburant` | 1 | AIDES_ETAT | remise générale à la pompe financée par l'État (précédent de 2022) plutôt que prix administré | 0 | 0.0 |  |
| `pole_public_bancaire` | 1 | AIDES_ETAT | établissement public soumis aux règles prudentielles et aux règles d'aides d'État (investisseur avisé) | 1 | 0.0 |  |

Tous les autres curseurs du simulateur (dépenses, prestations, IR, CSG, PFU, ISF, successions, SMIC, retraites, temps
de travail…) relèvent de la compétence nationale (niveau 0) ; leur seul canal européen est budgétaire (volet
préventif et PDE), traité au niveau du programme et non de la mesure.

## 5. Traduction macroéconomique

| canal | représentation | statut |
|---|---|---|
| Mesure de niveau 4 | retirée pour sa part non conforme (`Mesure.part_ue`) ; si la part est inconnue, mesure conservée et risque signalé | [D] qualification, [H] part |
| Contentieux (niveaux 1-2) | part non conforme retirée, mesure suspendue pendant le délai (première année reportée) | [H] |
| Amendes PDE | 0,05 % du PIB par semestre au plus, ajoutées aux dépenses publiques (calage « dépenses » de M8), sans effet de demande intérieure | [D] plafond, [H] durée |
| Sanctions de l'article 260 | non représentées : somme forfaitaire minimale de 12,46 M€ et astreinte de base de 3 000 € par jour (avant coefficients), négligeables à l'échelle macroéconomique | [D] |
| Prime de risque souveraine | choc sur l'écart OAT-Bund (`chocs_ecart_souverain` de M24), puis prime endogène avec les coefficients estimés sur l'échantillon incluant la crise 2010-2013 (0,0122 pt de taux par point de dette, −0,118 par point de solde) | [H] choc, [E] coefficients |
| Incertitude | variantes « conforme », « contentieux », « tension » | — |

Variantes prédéfinies (`SCENARIOS`) :
- **conforme** (référence de comparaison) : mesures de niveau 4 retirées pour leur part non conforme, aucune autre
  réponse ;
- **contentieux** : en plus, mesures de niveaux 1-2 réduites et reportées ;
- **tension** : contentieux + quatre semestres d'amende PDE au plafond (0,1 point de PIB en 2028 et 2029) + 50 pb
  d'écart souverain supplémentaire de 2027 à 2029 + prime de crise. Les 50 pb sont un ordre de grandeur à remplacer
  par l'utilisateur ; ils ne sont pas estimés.

## 6. Cartographie des incompatibilités du corpus

| mesure | candidat | règle | niveau | conséquence modélisée |
|---|---|---|---|---|
| TVA à 5,5 % sur les carburants (P10) | Le Pen | directive TVA (carburants hors annexe III ; fin des taux réduits sur combustibles fossiles en 2030) | 2 | conforme : même coût via une baisse d'accise ; contentieux : moitié retirée et report de deux ans |
| Baisse de la contribution à l'UE (P04) | Le Pen | décision ressources propres (unanimité) | 2 | contentieux : économie non réalisée |
| Économies « immigration » fondées sur la nationalité (P03) | Le Pen | non-discrimination (art. 18, 45 TFUE ; règlement 883/2004) | 4 | part non conforme inconnue : risque signalé, montant conservé |
| Préférence nationale (P16) | Le Pen | idem | 4 | non quantifiée |
| Contrôle des capitaux (L38) | Mélenchon | art. 63 TFUE | 4 | non quantifié |
| Taxe sur les multinationales (L08) | Mélenchon | conventions fiscales, pilier 2 | 1 | contentieux : report d'un an |
| Pôle public bancaire, livret A (L33, L37) | Mélenchon | aides d'État, règles prudentielles | 1 | non quantifié |
| Blocage du prix des carburants (L25) | Mélenchon | aides d'État (forme : remise générale) | 1 | non quantifié |
| Impôts de production −50 Md€ (H11) | Philippe | aides d'État : mesure générale | 0 | aucune |
| Règles d'or (P02, H02) | Le Pen, Philippe | cohérentes avec le volet préventif | 0 | régime M23 |
| Trajectoire de déficit (tous) | tous | PDE (France sous procédure depuis 2024) et volet préventif | 3 | variante « tension » |

## 7. Limites

- La qualification juridique est sommaire et ne remplace pas une analyse de juristes ; les cas « à instruire »
  restent signalés.
- Les réactions des marchés ne sont représentées que par la prime souveraine (pas de canal bancaire ni de change).
- Les conditionnalités des fonds européens (cohésion, facilité pour la reprise) ne sont pas représentées faute de
  montants vérifiés.
- Les renégociations (cadre financier pluriannuel, dérogations TVA) sont traitées comme des issues binaires.
