# 25 — Corpus des programmes présidentiels 2027 et correspondance avec le modèle

État au 2026-11-24. Code : `src/m27_corpus.py` (données structurées, sources, règles de conversion),
`src/m26_europe_institutions.py` (qualification européenne). Ce document décrit le corpus ; il ne contient aucune
évaluation ni appréciation des programmes.

## 1. Périmètre et choix des candidats

| Candidat | Document de référence | Chiffrage publié |
|---|---|---|
| Jean-Luc Mélenchon (LFI) | *L'Avenir en commun*, 5ᵉ édition (6 novembre 2026, 1 069 mesures dont 238 nouvelles) ; document budgétaire « Comment nous allons remettre de l'ordre dans les comptes publics » (14 octobre 2026) | année 2027 seulement : 106,4 Md€ de recettes, 81,7 Md€ de dépenses, 25 Md€ de réduction du déficit ; chiffrage complet promis début 2027 |
| Marine Le Pen (RN) | contre-budget et trajectoire (6 octobre 2026) ; réforme des retraites (17 novembre 2026) ; programme en ligne | enveloppe de 140 Md€ d'économies nettes d'ici 2032 ; postes partiellement chiffrés ; retraites 18,6 Md€ bruts en 2032 |
| Édouard Philippe (Horizons) | programme en ligne (15 thèmes, depuis le 12 novembre 2026) ; « volume 1 » (18 novembre 2026) | près de 150 Md€ d'économies et déficit < 2,5 % du PIB en fin de quinquennat ; mesures rarement chiffrées une à une ; « volume 2 » annoncé en janvier 2027 |

Candidat du centre : Édouard Philippe, parce que son programme est publié sous forme structurée et comporte un volet
de finances publiques ; pour Gabriel Attal, les sources consultées ne donnent qu'une enveloppe d'économies (120 à
150 Md€ selon les sources). Le corpus est extensible à d'autres candidats sans changement de code.

## 2. Règles de constitution

1. **Montant** : celui annoncé par le candidat (« candidat ») ; à défaut, chiffrage d'un tiers explicitement cité
   (« tiers ») ; sinon aucun montant (« aucun »). Signe : du point de vue du solde public (+ recette ou économie).
2. **Canal** : curseur(s) du simulateur. Quand le curseur n'est pas exprimé en Md€, sa valeur est obtenue en inversant
   le rendement statique du simulateur à partir du montant annoncé (PFU : 0,6 Md€ par point ; ISF : assiette 930 Md€
   moins l'IFI remplacé ; successions : 18 Md€ ; TVA : 8,2 Md€ par point de taux normal ; assurance chômage : 40 Md€ ;
   IS : rendement de référence de l'IS du modèle par point ; transferts : PIB nominal de 2027 de la référence). On
   simule ainsi la mesure *telle que chiffrée par le candidat* ; le modèle applique ensuite ses propres comportements
   (érosion d'assiette M13, bouclage macroéconomique), ce qui permet de comparer rendement annoncé et rendement simulé.
3. **Hypothèses de correspondance [H]** : toute convention qui ne découle pas du texte est écrite dans la règle de la
   mesure (section 4) et peut être remplacée par une variante.
4. **Quantifiable** : *oui* (montant et canal), *partiel* (canal identifié, montant ou périmètre manquant, ou canal
   approché), *non* (mesure institutionnelle, réglementaire ou sans canal dans le modèle).
5. **Calendrier** : première année d'application par mesure (`Mesure.debut`) ; la traduction (M25) accepte désormais
   des listes de mesures avec dates propres.
6. **Éléments de régime** : règles d'or et objectifs de solde ne sont pas des mesures mais des régimes budgétaires
   (M23) ; ils sont repérés (`Mesure.regime`).

## 3. Tables du corpus

### Jean-Luc Mélenchon (LFI)

| id | mesure | montant (Md€, signe solde) | chiffrage | calendrier | début modèle | canal du modèle | quantifiable | UE |
|---|---|---|---|---|---|---|---|---|
| L01 | Suppression du prélèvement forfaitaire unique (flat tax) | +9.0 (2027) | candidat | 2027 | 2027 | `pfu` 15 | oui | pfu (niv. 0) |
| L02 | Rétablissement d'un impôt sur la fortune renforcé | +10.0 (2027) | candidat | 2027 | 2027 | `isf` 1.31 | oui | isf (niv. 0) |
| L03 | Taxe Zucman (patrimoines supérieurs à 100 M€) | +15.0 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 15 | partiel | — |
| L04 | Réforme des droits de succession | +20.0 (2027) | candidat | la première année | 2027 | `successions` 111 | oui | successions (niv. 0) |
| L05 | Impôt sur le revenu à 14 tranches | — | aucun | au cours du mandat | 2027 | — | partiel | ir_t4 (niv. 0) |
| L06 | Rétablissement de la CVAE sur les plus grandes entreprises | +3.0 (2027) | candidat | 2027 | 2027 | `impots_production` 3 | oui | impots_production (niv. 0) |
| L07 | Réforme de l'impôt sur les sociétés | +3.0 (2027) | candidat | 2027 | 2027 | `taux_is` 3 Md€ (IS) | oui | taux_is (niv. 0) |
| L08 | Taxe universelle sur les multinationales | +5.0 (2027) | candidat | la première année | 2027 | `recettes_neutres` 5 | partiel | taxe_multinationales (niv. 1) |
| L09 | Renforcement de la taxe sur les services numériques (GAFAM) | +3.9 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 3.9 | partiel | recettes_neutres (niv. 0) |
| L10 | Taxe sur les superprofits | +5.0 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 5 | partiel | recettes_neutres (niv. 0) |
| L11 | Rabot et suppression des niches fiscales et sociales « les plus injustes » | +22.0 (2027) | candidat | 2027 | 2027 | `transferts_menages` -11 Md€; `cotisations_employeurs` 11 | partiel | recettes_neutres (niv. 0) |
| L12 | Fin des exonérations de cotisations au-dessus de 2 SMIC | — | aucun | — | 2027 | — | partiel | cotisations_employeurs (niv. 0) |
| L13 | Taxes sur les transactions financières | +5.0 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 5 | partiel | taxe_transactions_financieres (niv. 0) |
| L14 | Taxe sur les rachats d'actions | +2.5 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 2.5 | partiel | recettes_neutres (niv. 0) |
| L15 | Taxe sur les crypto-actifs | +1.0 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 1 | partiel | recettes_neutres (niv. 0) |
| L16 | Lutte contre la fraude fiscale | +2.0 (2027) | candidat | la première année | 2027 | `recettes_neutres` 2 | partiel | recettes_neutres (niv. 0) |
| L20 | Dégel et hausse de 10 % du point d'indice | -17.0 (2027) | candidat | 2027 | 2027 | `point_indice` 10 | oui | point_indice (niv. 0) |
| L21 | Revalorisation de 10 % des pensions, allocations familiales et APL | -8.0 (2027) | candidat | 2027 | 2027 | `transferts_menages` 8 Md€ | partiel | — |
| L22 | Logements d'urgence et réquisition de logements vacants | -3.0 (2027) | candidat | 2027 | 2027 | `autres_depenses` 3 | oui | — |
| L23 | Garantie d'autonomie pour les jeunes | -9.5 (2027) | candidat | 2027 | 2027 | `transferts_menages` 9.5 Md€ | oui | — |
| L24 | SMIC à 1 700 € net | — | aucun | — | 2027 | `smic` 15 | oui | smic (niv. 0) |
| L25 | Blocage du prix des carburants à 1,70 €/l | — | aucun | — | 2027 | — | partiel | blocage_prix_carburant (niv. 1) |
| L26 | 10 000 postes dans l'Éducation nationale | -0.5 (2027) | candidat | 2027 | 2027 | `education` 0.5 | oui | — |
| L27 | Gratuité de la cantine scolaire | -3.6 (2027) | candidat | 2027 | 2027 | `education` 3.6 | oui | — |
| L28 | 250 000 places à l'université | -3.5 (2027) | candidat | 2027 | 2027 | `education` 3.5 | oui | — |
| L29 | Hôpital public (+10 000 postes soignants) | -3.0 (2027) | candidat | 2027 | 2027 | `sante` 3 | oui | — |
| L30 | Violences sexistes et sexuelles ; violences faites aux enfants | -4.6 (2027) | candidat | 2027 | 2027 | `autres_depenses` 4.6 | oui | — |
| L31 | Indexation des budgets 2027 des services supprimés en 2026 | -7.0 (2027) | candidat | 2027 | 2027 | `autres_depenses` 7 | oui | — |
| L32 | Adaptation au dérèglement climatique | -10.0 (2027) | candidat | dès 2026 | 2027 | `investissement_public` 10 | oui | — |
| L33 | Investissements de planification écologique portés par le pôle public bancaire | — | candidat | par an, hors budget de l'État | 2028 | `investissement_hors_apu` 100 | partiel | pole_public_bancaire (niv. 1) |
| L34 | Abrogation de la réforme de 2023 (retour à 62 ans) | -9.0 (2027) | candidat | dès l'année suivant l'élection | 2027 | `age_legal_immediat` 62 | oui | — |
| L35 | Abrogation des réformes de l'assurance chômage | -3.0 (2027) | candidat | dès l'année suivant l'élection | 2027 | `assurance_chomage` 7.5 | oui | — |
| L36 | Retour à 60 ans avec 40 annuités | — | aucun | en un mandat | 2028 | `age_legal` 60 | partiel | — |
| L37 | Plafond du livret A relevé à 30 000 € ; centralisation portée à 80 % ; livret B | — | aucun | — | 2027 | — | non | pole_public_bancaire (niv. 1) |
| L38 | Contrôle des capitaux ; fin de la cotation continue | — | aucun | — | 2027 | — | non | controle_capitaux (niv. 4) |
| L39 | Réduction du déficit de 25 Md€ par an ; stabilisation de la dette en un quinquennat | — | candidat | 2027-2032 | 2027 | régime : objectif | non | — |

### Marine Le Pen (RN)

| id | mesure | montant (Md€, signe solde) | chiffrage | calendrier | début modèle | canal du modèle | quantifiable | UE |
|---|---|---|---|---|---|---|---|---|
| P01 | 140 Md€ d'économies nettes d'ici 2032 ; dette de 121 % (2027) à 112 % (2032) ; déficit à 3 % en 2030 ; 30 Md€ de baisses d'impôts | +140.0 (2032) | candidat | 2027-2032 | 2027 | régime : objectif | non | — |
| P02 | Règle d'or constitutionnelle par référendum (déficit plafonné au niveau stabilisant la dette) | — | candidat | dans les 12 mois | 2027 | régime : R1_actif | non | regle_or_constitutionnelle (niv. 0) |
| P03 | Économies sur le « coût de l'immigration » | +15.0 (2027) | candidat | 15 Md€ en 2027, 29 Md€ en année pleine | 2027 | `transferts_menages` -15 Md€ | partiel | preference_nationale (niv. 4) |
| P04 | Baisse de la contribution au budget de l'Union | +9.0 (2027) | candidat | 2027 | 2027 | `recettes_neutres` 9 | oui | contribution_ue_reduite (niv. 2) |
| P05 | Réorganisation de l'État (centralisation de la TVA, transferts aux collectivités et à la Sécurité sociale votés par le Parlement) | +20.7 (2027) | candidat | dès 2027 | 2027 | `autres_depenses` -20.7 | partiel | — |
| P06 | Contribution des collectivités (dont suppression des EPCI et métropoles 0,25 Md€, effectifs 0,8 Md€) | +8.2 (2027) | candidat | 2027 | 2027 | — | partiel | — |
| P07 | Agences de l'État | +3.4 (2027) | candidat | 2027 | 2027 | — | partiel | — |
| P08 | Âge légal ramené à 62 ans (60 ans pour les carrières commencées avant 20 ans), 42 annuités ; pilier de capitalisation obligatoire (socle : Fonds de réserve pour les retraites) | -18.6 (2032) | candidat | application au 1er janvier 2028 | 2028 | `age_legal` 62 | partiel | — |
| P09 | Économies sur les retraites (« corrections de mesures injustes ») | +17.5 (2032) | candidat | à terme | 2027 | — | partiel | — |
| P10 | TVA ramenée de 20 % à 5,5 % sur l'électricité, le gaz, le fioul et les carburants | -10.0 (2022) | tiers | — | 2027 | `tva` -1.22 | partiel | tva_energie_carburants (niv. 2) |
| P11 | Exonération d'impôt sur le revenu des moins de 30 ans (jusqu'à 4 SMIC) | -2.0 (2027) | candidat | — | 2027 | `transferts_menages` 2 Md€ | oui | — |
| P12 | Permis de conduire gratuit (18 ans, casier vierge) ; prime d'activité étudiante | -1.3 (2027) | candidat | — | 2027 | `transferts_menages` 1.3 Md€ | oui | — |
| P13 | Part fiscale pleine dès le deuxième enfant | -3.5 (2027) | candidat | 2027 | 2027 | `transferts_menages` 3.5 Md€ | oui | — |
| P14 | Dons familiaux défiscalisés ; prêt à taux zéro au troisième enfant ; suppression de la CVEC | — | aucun | — | 2027 | — | partiel | — |
| P15 | Suppression de la CFE et des impôts de production « qui nuisent à la relocalisation » | — | aucun | — | 2027 | `impots_production` à préciser | partiel | impots_production (niv. 0) |
| P16 | Priorité nationale (logement, emploi, prestations) | — | aucun | — | 2027 | — | non | preference_nationale (niv. 4) |

### Édouard Philippe (Horizons)

| id | mesure | montant (Md€, signe solde) | chiffrage | calendrier | début modèle | canal du modèle | quantifiable | UE |
|---|---|---|---|---|---|---|---|---|
| H01 | Près de 150 Md€ d'économies ; déficit sous 2,5 % du PIB en fin de quinquennat ; moitié de l'effort sur les dépenses sociales, un quart sur l'État et les collectivités, un quart sur la croissance | +150.0 (2032) | candidat | quinquennat | 2027 | régime : objectif | non | — |
| H02 | Règle d'or constitutionnelle par référendum ; aucun nouvel impôt pendant cinq ans | — | candidat | dès le début du quinquennat | 2027 | régime : R2_actif_depenses | non | regle_or_constitutionnelle (niv. 0) |
| H03 | 250 000 postes de fonctionnaires en moins (un départ sur trois non remplacé dans les fonctions de bureau) | — | aucun | quinquennat | 2027 | `emploi_public` -250 | oui | — |
| H04 | Hausse de 20 % du salaire des enseignants | — | aucun | quinquennat | 2027 | — | partiel | — |
| H05 | Âge de départ à 65 ans et 45 annuités ; départ précoce pour un tiers des assurés ; capitalisation collective | — | aucun | non précisé | 2028 | `age_legal` 65 | partiel | — |
| H06 | Fin des 35 heures ; deux heures supplémentaires hebdomadaires exonérées de cotisations | — | aucun | ordonnances de juillet 2027 | 2027 | `temps_travail` 37 | partiel | — |
| H07 | Indemnisation limitée à 12 mois pour les moins de 50 ans | — | aucun | — | 2027 | `assurance_chomage` à préciser | partiel | — |
| H08 | Baisse de 30 % du nombre d'allocataires du RSA (accompagnement, métiers en tension) | — | aucun | — | 2027 | `rsa` -30 | partiel | — |
| H09 | Trois jours de carence pour tous (public et privé) | — | aucun | — | 2027 | — | non | — |
| H10 | Allocation de 350 € par mois dès le premier enfant, dégressive ; exonération d'impôt les trois premières années de l'enfant ; suppression des frais de notaire au premier achat (< 35 ans) ; prêt à taux zéro famille | — | aucun | — | 2027 | — | partiel | — |
| H11 | Baisse de 50 Md€ des impôts de production financée par 50 Md€ de baisse des aides aux entreprises | +0.0 (2028) | candidat | dès la première loi de finances, pacte pluriannuel | 2028 | `impots_production` -25; `cotisations_employeurs` 25 | partiel | impots_production (niv. 0) |
| H12 | Fonds unique d'adaptation au changement climatique | -2.0 (2027) | candidat | par an | 2027 | `investissement_public` 2 | oui | — |
| H13 | Fusion, suppression ou privatisation d'une trentaine d'agences (dont France Travail) | — | aucun | — | 2027 | — | partiel | — |
| H14 | Huit réacteurs nucléaires supplémentaires ; suppression du ZAN | — | aucun | — | 2027 | — | non | — |

## 4. Règles de conversion et hypothèses par mesure

- **L01** : Points de PFU = montant / 0,6 Md€ par point (assiette 60 Md€).
- **L02** : Taux moyen = (montant + rendement de l'IFI remplacé) / assiette ISF 930 Md€.
- **L03** : [H] Assiette (> 100 M€) distincte de celle de l'ISF du modèle : recette sans effet de demande (propension à consommer quasi nulle) ; l'érosion d'assiette n'est pas représentée (le montant annoncé est une borne haute). Variante : canal isf (érosion M13).
- **L04** : Variation du rendement = montant / 18 Md€ (au-delà de la borne de l'interface).
- **L05** : Barème non publié : canal ir_t1..ir_t4 identifié, paramètres manquants.
- **L06** : Md€ directs.
- **L07** : Paramètres non publiés : taux_is calé sur 3 Md€ par le rendement de référence de l'IS du modèle (fonction conversion_is).
- **L08** : [H] Recette sans effet de demande intérieure (bénéfices en grande partie distribués aux non-résidents).
- **L09** : [H] idem L08.
- **L10** : [H] Prélèvement exceptionnel sur profits.
- **L11** : [H] Composition non publiée : moitié ménages (baisse de revenu disponible), moitié entreprises (hausse du coût du travail). Variante : recettes_neutres.
- **L12** : Canal cotisations_employeurs ; montant non publié.
- **L20** : Point d'indice +10 %.
- **L21** : [H] Le montant annoncé (8 Md€) n'est pas compatible avec une revalorisation générale de toutes les pensions (masse de plusieurs centaines de Md€) : périmètre à préciser ; montant annoncé versé en transferts non ciblés. Variante : allocations_familiales et aides_logement +10 % (microsimulation).
- **L23** : [H] Transfert non ciblé (pas de mesure jeunes dans M4).
- **L24** : Hausse = 1 700 / 1 477,93 − 1 ≈ 15,0 % (SMIC net au 1er juin 2026).
- **L25** : Coût dépendant du prix de marché : canal energie_import + subvention, non chiffrable sans hypothèse de prix.
- **L27** : [H] Dépense de fonctionnement (transfert en nature).
- **L30** : 2,6 + 2,0 Md€.
- **L33** : 100 Md€ par an annoncés hors budget : investissement hors APU (effet de demande sans coût pour le solde public). [H] Montée en charge non précisée : appliqué dès 2028 ; additionnalité totale (borne haute). Financement, dette du pôle public et effet d'offre non représentés.
- **L34** : Coût calculé par M9 (le montant annoncé sert de contrôle).
- **L35** : Variation = montant / 40 Md€ de dépense.
- **L36** : Objectif de mandat : variante (non incluse dans le paquet 2027).
- **L37** : Pas de canal de l'intermédiation financière dans le modèle.
- **L38** : Mesures de régulation sans canal.
- **L39** : Objectif de solde : élément de régime (pas de règle automatique).
- **P01** : Enveloppe agrégée : les mesures détaillées ci-dessous en couvrent une partie.
- **P02** : Élément de régime : règle de stabilisation (M23 R1, mode actif).
- **P03** : [H] Composition non publiée : baisse de prestations (transferts). La part fondée sur la nationalité est incompatible pour les ressortissants de l'Union (M26, niveau 4) ; cette part n'est pas connue.
- **P04** : Recette nette sans effet de demande.
- **P05** : [H] Les sources ne disent pas si les économies sur les collectivités (P06) et les agences (P07) sont incluses : par prudence, P06 et P07 sont traitées comme des composantes de P05 (non additionnées).
- **P06** : Composante de P05 [H].
- **P07** : Composante de P05 [H] ; une commission sénatoriale évaluait ces économies à environ 0,5 Md€.
- **P08** : Coût brut annoncé 18,6 Md€ en 2032. Carrières longues, durée et pilier de capitalisation non représentés dans M9 (extension identifiée, doc 26).
- **P09** : Fourchette 15-20 Md€, mesures non détaillées.
- **P10** : Coût : ordre de grandeur de l'Institut Montaigne (2022), aucun montant du candidat dans les sources. [H] Baisse équivalente du taux normal (le modèle ne distingue pas l'énergie) : la répercussion sur les prix est répartie sur toute la consommation.
- **P11** : [H] Baisse d'impôt traitée en transfert non ciblé.
- **P12** : 0,7 + 0,6 Md€.
- **P13** : [H] Transfert non ciblé.
- **P15** : Montant non publié : canal impots_production.
- **H01** : Enveloppe agrégée.
- **H02** : Élément de régime : trajectoire de rétablissement (M23 R2, mode actif, instruments de dépense).
- **H03** : Effectif atteint en 5 ans ; coût moyen du simulateur 56 k€ par agent.
- **H04** : Masse salariale des enseignants non disponible dans le modèle : canal education (Md€) à chiffrer.
- **H05** : Durée d'assurance, départs précoces et capitalisation non représentés dans M9.
- **H06** : [H] Durée de référence portée à 37 h (2 h supplémentaires) ; exonération non chiffrée.
- **H07** : Le curseur agit sur les montants, pas sur la durée : montant à chiffrer.
- **H08** : [H] Le curseur réduit le montant forfaitaire (−30 %) : approximation budgétaire d'une baisse des effectifs ; la réponse de participation passe par M15 (gain à l'emploi accru), pas par l'accompagnement annoncé ; effet distributif différent d'une baisse d'effectifs.
- **H09** : Pas de canal des indemnités journalières.
- **H10** : Barèmes non publiés.
- **H11** : [H] Composition des aides non publiée. Le modèle représente une aide supprimée de deux façons : (a) aide assimilable à une moindre imposition de la production (subventions, dépenses fiscales) : même canal que les impôts de production, de signe opposé, donc effet net nul ; (b) allègement de cotisations supprimé : hausse du coût du travail (cotisations_employeurs). Central : moitié (a), moitié (b), soit impôts de production −25 Md€ nets et cotisations +25 Md€. Variantes : (a) seul (mesure neutre dans le modèle) ; (b) seul (impôts de production −50, cotisations +50). Limite : le modèle ne distingue pas les distorsions propres aux impôts de production de celles des subventions (argument central du candidat). Début : première loi de finances du quinquennat (2028).

## 5. Bilan de couverture

| Candidat | mesures | quantifiables | partielles | non quantifiables | montants chiffrés (Md€, hors composantes) | dont avec canal | enveloppe globale annoncée |
|---|---|---|---|---|---|---|---|
| Jean-Luc Mélenchon (LFI) | 36 | 18 | 15 | 3 | 188.1 | 188.1 | solde 2027 : +24,7 Md€ |
| Marine Le Pen (RN) | 16 | 4 | 9 | 3 | 97.6 | 80.1 | 140 Md€ d'économies nettes d'ici 2032 |
| Édouard Philippe (Horizons) | 14 | 2 | 8 | 4 | 2.0 | 2.0 | ≈ 150 Md€ d'économies, déficit < 2,5 % en 2032 |

Lecture : le paquet 2027 de LFI est entièrement chiffré par le candidat (recettes et dépenses se recoupent exactement
avec les totaux de 106,4 et 81,7 Md€) ; les programmes RN et Horizons sont décrits par des enveloppes agrégées dont
la composition n'est que partiellement publiée. Pour ces deux candidats, une part importante de l'effort annoncé
(économies non ventilées) ne peut entrer dans le modèle que comme hypothèse de composition, ou comme objectif de solde
atteint par la règle budgétaire de M23 (variante « programme = régime »). Les deux lectures devront être présentées
côte à côte dans le rapport.

Mesures non quantifiables dans le modèle (principales) : contrôle des capitaux, fin de la cotation continue,
centralisation de l'épargne réglementée et pôle public bancaire (LFI) ; préférence nationale (RN) ; jours de carence,
nucléaire, ZAN, réorganisation des agences (Horizons) ; piliers de capitalisation (RN, Horizons) ; paramètres fins des
réformes de retraite (durée d'assurance, carrières longues). Voir la liste priorisée des mécanismes manquants (doc 26).

## 6. Points de vigilance relevés pendant la constitution

- **L21** : 8 Md€ pour « 10 % sur les pensions, allocations familiales et APL » n'est pas compatible avec une
  revalorisation générale des pensions ; le périmètre devra être confirmé par le chiffrage complet annoncé.
- **P05-P07** : la décomposition des économies de « réorganisation de l'État » (20,7 Md€) n'indique pas si les
  contributions des collectivités (8,2 Md€) et des agences (3,4 Md€) sont incluses ; traitées comme composantes.
- **P10** : aucun coût n'est publié par le candidat ; ordre de grandeur de l'Institut Montaigne (2022), à actualiser.
- **H11** : l'échange impôts de production contre aides aux entreprises est neutre en montant mais pas en effets selon
  la nature des aides supprimées (subventions, dépenses fiscales, allègements) ; deux variantes.
- **Dates** : les sources de presse se contredisent parfois sur les dates (ex. publication de *L'Avenir en commun*) ;
  on retient les documents des candidats.

## 7. Sources

- `LFI_BUDGET` : https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf
- `LFI_AEC` : https://melenchon2027.fr/?p=24158
- `LFI_PRESSE` : https://melenchon2027.fr/wp-content/uploads/2026/11/DOSSIER-DE-PRESSE_0611_PROGRAMME_ST.pdf
- `LFI_LCP_BUDGET` : https://lcp.fr/actualites/contre-budget-lfi-propose-1064-milliards-d-euros-de-recettes-supplementaires-et-817
- `LFI_EPARGNE` : https://lessentieldeleco.fr/9362-melenchon-epargne/
- `RN_PS_BUDGET` : https://www.publicsenat.fr/actualites/politique/140-milliards-deuros-deconomies-dici-2032-leffort-radical-propose-par-marine-le-pen-pour-redresser-les-f
- `RN_LCP_JEUNES` : https://lcp.fr/actualites/permis-de-conduire-gratuit-exoneration-d-impot-jusqu-a-30-ans-comment-le-rn-veut
- `RN_MONEYVOX` : https://www.moneyvox.fr/impot/actualites/110673/140-milliards-economies-ce-quil-faut-retenir-de-intervention-de-marine-le-pen
- `RN_RETRAITES_PS` : https://www.publicsenat.fr/actualites/politique/presidentielle-2027-que-contient-la-reforme-des-retraites-presentee-par-marine-le-pen
- `RN_RETRAITES_SUD` : https://www.sudradio.fr/sud-radio/age-de-depart-cotisation-et-capitalisation-les-propositions-du-rn-pour-reformer-les-retraites
- `RN_RETRAITES_BRUT` : https://www.brut.media/fr/articles/le-pen-affirme-que-sa-reforme-des-retraites-sera-engagee-des-son-arrivee-au-pouvoir-et-sera-appliquee-au-1er-janvier-2028
- `RN_ENERGIE` : https://www.les-energies-renouvelables.eu/article/actualites/energies/baisse-de-la-tva-arret-du-photovoltaique-ce-que-le-programme-energie-du-rn-changerait-pour-les-menages-2302/
- `RN_VOTONS` : https://votons-2027.fr/candidats/le-pen/programme
- `MONTAIGNE_TVA_2022` : https://www.institutmontaigne.org/presidentielle-2022/marine-le-pen/baisser-la-tva-de-20-a-55-pour-les-carburants-lelectricite-le-gaz-et-le-fioul-domestique
- `EP_COMPTES` : https://www.edouardphilippe.fr/programme/comptes-publics
- `EP_PS_VOL1` : https://www.publicsenat.fr/actualites/politique/capitalisation-suppression-de-250-000-postes-de-fonctionnaires-autonomie-des-ecoles-fin-des-35-heures-aides-pour-les-familles-edouard-philippe-presente-son-projet-massif-et
- `EP_EURONEWS` : https://fr.euronews.com/2026/10/09/presidentielle-2027-edouard-philippe-mise-sur-le-travail-et-la-reduction-des-depenses-publ
- `EP_DEAL` : https://www.publicsenat.fr/actualites/economie/entreprises-un-deal-a-250-milliards-deuros-sur-un-quinquennat-que-represente-la-proposition-dedouard-philippe
- `SMIC_2026` : https://www.info.gouv.fr/public/index.php/actualite/le-smic-revalorise-le-1er-juin-2026

Sources complémentaires de vérification : pages programmes de votons-2027.fr (agrégateur citant les sources
officielles), LCP, Public Sénat, Euronews (dates et montants).
