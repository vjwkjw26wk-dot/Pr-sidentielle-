# Présentation détaillée des programmes politiques {#sec:programmes}

Ce chapitre présente les trois programmes tels qu'ils sont publiés, puis leur traduction dans le modèle. Deux règles
le gouvernent. D'une part, **les montants, calendriers et effets attendus sont ceux annoncés par les candidats** ou,
à défaut, des chiffrages de tiers explicitement cités ; aucun montant n'est inventé. D'autre part, **les hypothèses de
traduction de l'auteur du modèle sont distinguées des engagements des candidats** : elles sont marquées [H] et
accompagnées de variantes. Le corpus est daté du 24 novembre 2026 ; il est structuré dans le module M27 et régénérable
(annexe \ref{sec:annexe-c}).

## Méthode de constitution du corpus {#sec:methode-corpus}

Pour chaque candidat, les sources primaires (programme, documents budgétaires, conférences de presse publiées sur les
sites des candidats) ont été privilégiées ; les articles de presse (Public Sénat, LCP, Euronews, Moneyvox, Sud Radio)
servent à dater et à compléter les annonces orales. Chaque mesure est décrite par : la source, le montant annoncé
(signe du point de vue du solde public : positif pour une recette ou une économie), le statut du chiffrage (par le
candidat, par un tiers, aucun), le calendrier, les bénéficiaires, le canal du modèle, la règle de conversion, le degré
de quantification (*oui*, *partiel*, *non*) et la qualification au regard du droit européen (chapitre
\ref{sec:europe}).

**Conversion des montants en paramètres.** Quand le paramètre du modèle n'est pas exprimé en euros (taux du
prélèvement forfaitaire unique, taux moyen de l'impôt sur la fortune, variation des droits de succession, taux de TVA,
taux de l'impôt sur les sociétés), sa valeur est obtenue en inversant le rendement **statique** du simulateur à partir
du montant annoncé. On simule ainsi la mesure *telle que le candidat la chiffre* ; le modèle applique ensuite ses
propres réactions (érosion d'assiette, bouclage macroéconomique). L'écart entre le rendement annoncé et le rendement
simulé est donc un résultat, et non une hypothèse.

| Candidat | Mesures du corpus | quantifiables | partielles | non quantifiables | montants chiffrés (Md€) | dont avec canal dans le modèle |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) | 36 | 18 | 15 | 3 | 188,1 | 188,1 |
| Le Pen (RN) | 16 | 4 | 9 | 3 | 97,6 | 80,1 |
| Philippe (Horizons) | 14 | 2 | 8 | 4 | 2,0 | 2,0 |

## Jean-Luc Mélenchon (La France insoumise) {#sec:prog-lfi}

**Vision économique et sociale.** *L'Avenir en commun* se présente comme un programme de « rupture avec l'ordre
économique » néolibéral, organisé en six « ruptures » dont la première est la « bifurcation écologique ». La doctrine
économique est explicitement keynésienne et redistributive : relancer l'activité par les revenus des classes
populaires et les services publics, financer cette relance par l'imposition du capital, des hauts patrimoines et des
grandes entreprises, et planifier la transition écologique en mobilisant un pôle public bancaire. Le document
budgétaire du 14 octobre 2026 précise : « Si vous nous jugez d'après les critères du néolibéralisme, nos projets sont
inacceptables » (citation rapportée par LCP).

**Principaux objectifs chiffrés.** Pour 2027 : 106,4 Md€ de recettes supplémentaires, 81,7 Md€ de dépenses nouvelles,
soit une réduction du déficit de 24,7 Md€ ; stabilisation du ratio de dette sur un quinquennat ; « retour de
l'activité et redressement des comptes » dès 2028 (formulation du document). Le document précise lui-même qu'il « ne
constitue pas un chiffrage complet » du programme, promis pour le début de 2027.

**Mesures fiscales.** Suppression du prélèvement forfaitaire unique (9 Md€), rétablissement d'un impôt sur la fortune
renforcé (10 Md€), taxe sur les patrimoines supérieurs à 100 M€ (15 Md€), réforme des droits de succession (20 Md€
la première année), impôt sur le revenu à 14 tranches (non chiffré), rétablissement de la CVAE sur les plus grandes
entreprises (3 Md€), réforme de l'impôt sur les sociétés (3 Md€), taxe universelle sur les multinationales (5 Md€),
renforcement de la taxe sur les services numériques (3,9 Md€), taxe sur les superprofits (5 Md€), rabot des niches
fiscales et sociales « les plus injustes » (22 Md€), taxes sur les transactions financières (5 Md€), les rachats
d'actions (2,5 Md€) et les crypto-actifs (1 Md€), lutte contre la fraude (2 Md€).

**Dépenses publiques et services publics.** Dégel et hausse de 10 % du point d'indice (17 Md€), 10 000 postes dans
l'Éducation nationale (0,5 Md€), gratuité de la cantine (3,6 Md€), 250 000 places à l'université (3,5 Md€), hôpital
public (3 Md€), lutte contre les violences sexistes, sexuelles et faites aux enfants (4,6 Md€), indexation des budgets
des services supprimés en 2026 (7 Md€).

**Protection sociale et retraites.** Abrogation de la réforme de 2023 (9 Md€) et des réformes de l'assurance chômage
(3 Md€) ; revalorisation de 10 % des pensions, allocations familiales et aides au logement (8 Md€) ; garantie
d'autonomie pour les jeunes (9,5 Md€) ; objectif de mandat : retraite à 60 ans avec 40 annuités, pension minimale
alignée sur le SMIC pour une carrière complète (non chiffrés).

**Emploi et salaires.** SMIC à 1 700 € net (non chiffré ; soit +15,0 % par rapport au SMIC net de 1 477,93 € au
1er juin 2026), conférence sur les salaires et indexation généralisée (non chiffrées).

**Entreprises, investissement et industrie ; énergie et transition.** Planification écologique : 10 Md€ pour
l'adaptation au dérèglement climatique, 700 000 rénovations par an (non chiffré), et 100 Md€ par an d'investissements
« portés par le pôle public bancaire » hors budget de l'État ; blocage du prix des carburants à 1,70 €/l (non
chiffré).

**Commerce extérieur et souveraineté ; finance.** Contrôle des capitaux, fin de la cotation continue en Bourse,
relèvement du plafond du livret A à 30 000 € et de la centralisation de l'épargne réglementée, création d'un
« livret B » (non chiffrés).

**Politique budgétaire et financement.** Le financement repose sur les recettes nouvelles ; 25 Md€ par an sont
annoncés pour la réduction du déficit. Le document ne précise ni hypothèse de croissance pour 2027, ni multiplicateur.

**Bénéficiaires et perdants potentiels (premier ordre).** Bénéficiaires : agents publics, ménages modestes et jeunes
(transferts, SMIC, cantine), retraités (revalorisations, âge), demandeurs d'emploi. Contributeurs : détenteurs de
patrimoines élevés et de revenus du capital, héritiers, grandes entreprises et multinationales, bénéficiaires des niches
supprimées (composition non publiée). Les effets indirects (prix, emploi, compétitivité) sont analysés aux chapitres
\ref{sec:transmission} et \ref{sec:resultats}.

**Traduction dans le modèle.** Le paquet 2027 est entièrement traduit ; les montants recoupent exactement les totaux
publiés. Les principales hypothèses de traduction sont :

- les recettes sans canal propre (taxe sur les très grands patrimoines, multinationales, numérique, superprofits,
  transactions financières, rachats d'actions, crypto-actifs, fraude) sont traitées comme des recettes sans effet direct
  sur la demande intérieure [H] ; l'érosion de leur assiette n'est pas représentée : leurs montants sont des bornes
  hautes ;
- les 22 Md€ de niches, dont la composition n'est pas publiée, sont répartis pour moitié sur les ménages et pour
  moitié sur le coût du travail [H] ;
- la revalorisation de 10 % (8 Md€) est versée en transferts non ciblés : le montant annoncé n'est pas compatible
  avec une revalorisation générale de toutes les pensions (masse de plusieurs centaines de Md€), ce qui suggère un
  périmètre plus restreint, à préciser [H] ;
- les 100 Md€ du pôle public bancaire sont traités comme un investissement hors administrations publiques, appliqué à
  partir de 2028, avec une additionnalité totale (borne haute) [H] ;
- la réforme des retraites est simulée par M9 (retour immédiat à 62 ans, calendrier de durée de la loi de 2014) ; le
  coût annoncé (9 Md€) sert de contrôle.


**Tableau : mesures du corpus — Mélenchon (LFI).** Montants en Md€ (signe du point de vue du solde public), année de référence entre parenthèses ; « début » : première année d'application dans le modèle ; UE : niveau de qualification (chapitre \ref{sec:europe}).

| id | mesure | montant | chiffrage | début | traduction dans le modèle | quant. | UE |
|---|---|---|---|---|---|---|---|
| L01 | Suppression du prélèvement forfaitaire unique (flat tax) | +9,0 (2027) | candidat | 2027 | `pfu` +15,00 | oui | 0 |
| L02 | Rétablissement d'un impôt sur la fortune renforcé | +10,0 (2027) | candidat | 2027 | `isf` +1,31 | oui | 0 |
| L03 | Taxe Zucman (patrimoines supérieurs à 100 M€) | +15,0 (2027) | candidat | 2027 | `recettes_neutres` +15,00 | partiel | — |
| L04 | Réforme des droits de succession | +20,0 (2027) | candidat | 2027 | `successions` +111,11 | oui | 0 |
| L05 | Impôt sur le revenu à 14 tranches | — | aucun | 2027 | — | partiel | 0 |
| L06 | Rétablissement de la CVAE sur les plus grandes entreprises | +3,0 (2027) | candidat | 2027 | `impots_production` +3,00 | oui | 0 |
| L07 | Réforme de l'impôt sur les sociétés | +3,0 (2027) | candidat | 2027 | `taux_is` +3,0 Md€ | oui | 0 |
| L08 | Taxe universelle sur les multinationales | +5,0 (2027) | candidat | 2027 | `recettes_neutres` +5,00 | partiel | 1 |
| L09 | Renforcement de la taxe sur les services numériques (GAFAM) | +3,9 (2027) | candidat | 2027 | `recettes_neutres` +3,90 | partiel | 0 |
| L10 | Taxe sur les superprofits | +5,0 (2027) | candidat | 2027 | `recettes_neutres` +5,00 | partiel | 0 |
| L11 | Rabot et suppression des niches fiscales et sociales « les plus injustes » | +22,0 (2027) | candidat | 2027 | `transferts_menages` −11,0 Md€; `cotisations_employeurs` +11,00 | partiel | 0 |
| L12 | Fin des exonérations de cotisations au-dessus de 2 SMIC | — | aucun | 2027 | — | partiel | 0 |
| L13 | Taxes sur les transactions financières | +5,0 (2027) | candidat | 2027 | `recettes_neutres` +5,00 | partiel | 0 |
| L14 | Taxe sur les rachats d'actions | +2,5 (2027) | candidat | 2027 | `recettes_neutres` +2,50 | partiel | 0 |
| L15 | Taxe sur les crypto-actifs | +1,0 (2027) | candidat | 2027 | `recettes_neutres` +1,00 | partiel | 0 |
| L16 | Lutte contre la fraude fiscale | +2,0 (2027) | candidat | 2027 | `recettes_neutres` +2,00 | partiel | 0 |
| L20 | Dégel et hausse de 10 % du point d'indice | −17,0 (2027) | candidat | 2027 | `point_indice` +10,00 | oui | 0 |
| L21 | Revalorisation de 10 % des pensions, allocations familiales et APL | −8,0 (2027) | candidat | 2027 | `transferts_menages` +8,0 Md€ | partiel | — |
| L22 | Logements d'urgence et réquisition de logements vacants | −3,0 (2027) | candidat | 2027 | `autres_depenses` +3,00 | oui | — |
| L23 | Garantie d'autonomie pour les jeunes | −9,5 (2027) | candidat | 2027 | `transferts_menages` +9,5 Md€ | oui | — |
| L24 | SMIC à 1 700 € net | — | aucun | 2027 | `smic` +15,03 | oui | 0 |
| L25 | Blocage du prix des carburants à 1,70 €/l | — | aucun | 2027 | — | partiel | 1 |
| L26 | 10 000 postes dans l'Éducation nationale | −0,5 (2027) | candidat | 2027 | `education` +0,50 | oui | — |
| L27 | Gratuité de la cantine scolaire | −3,6 (2027) | candidat | 2027 | `education` +3,60 | oui | — |
| L28 | 250 000 places à l'université | −3,5 (2027) | candidat | 2027 | `education` +3,50 | oui | — |
| L29 | Hôpital public (+10 000 postes soignants) | −3,0 (2027) | candidat | 2027 | `sante` +3,00 | oui | — |
| L30 | Violences sexistes et sexuelles ; violences faites aux enfants | −4,6 (2027) | candidat | 2027 | `autres_depenses` +4,60 | oui | — |
| L31 | Indexation des budgets 2027 des services supprimés en 2026 | −7,0 (2027) | candidat | 2027 | `autres_depenses` +7,00 | oui | — |
| L32 | Adaptation au dérèglement climatique | −10,0 (2027) | candidat | 2027 | `investissement_public` +10,00 | oui | — |
| L33 | Investissements de planification écologique portés par le pôle public bancaire | — | candidat | 2028 | `investissement_hors_apu` +100,00 | partiel | 1 |
| L34 | Abrogation de la réforme de 2023 (retour à 62 ans) | −9,0 (2027) | candidat | 2027 | `retraites` : age=62, mode=immediat, duree=2014 | oui | — |
| L35 | Abrogation des réformes de l'assurance chômage | −3,0 (2027) | candidat | 2027 | `assurance_chomage` +7,50 | oui | — |
| L36 | Retour à 60 ans avec 40 annuités | — | aucun | 2028 | `retraites` : age=60, mode=progressif, duree=160, duree_mode=progressif | partiel | — |
| L37 | Plafond du livret A relevé à 30 000 € ; centralisation portée à 80 % ; livret B | — | aucun | 2027 | — | non | 1 |
| L38 | Contrôle des capitaux ; fin de la cotation continue | — | aucun | 2027 | — | non | 4 |
| L39 | Réduction du déficit de 25 Md€ par an ; stabilisation de la dette en un quinquennat | — | candidat | 2027 | régime (objectif) | non | — |

## Marine Le Pen (Rassemblement national) {#sec:prog-rn}

**Vision économique et sociale.** Le programme combine une ligne de défense du pouvoir d'achat (baisse de la TVA sur
l'énergie, mesures pour les jeunes et les familles, retour partiel sur la réforme des retraites), une attention aux
entreprises (suppression de la CFE et des impôts de production « qui nuisent à la relocalisation »), une priorité
nationale (logement, emploi, prestations) et un objectif de redressement des comptes fondé sur des économies ciblées :
immigration, contribution au budget européen, organisation de l'État et des collectivités. La presse a souligné
l'évolution du discours vers une ligne plus libérale qu'en 2022 tout en restant attachée à la redistribution
(franceinfo).

**Principaux objectifs chiffrés.** 140 Md€ d'économies nettes d'ici 2032 (présentées le 6 octobre 2026) ; dette
ramenée de 121 % du PIB en 2027 à 112 % en 2032 ; déficit à 3 % du PIB en 2030 ; 30 Md€ de baisses d'impôts ; règle
d'or constitutionnelle par référendum dans les douze mois, plafonnant le déficit au niveau qui stabilise la dette.

**Mesures fiscales.** TVA ramenée de 20 % à 5,5 % sur l'électricité, le gaz, le fioul et les carburants (coût non
publié par le candidat ; ordre de grandeur de l'Institut Montaigne en 2022 : une dizaine de Md€ ; d'autres estimations
de presse vont jusqu'à 15-18 Md€) ; exonération d'impôt sur le revenu des moins de 30 ans jusqu'à quatre fois le SMIC
(2 Md€) ; part fiscale pleine dès le deuxième enfant (3,5 Md€ en 2027) ; défiscalisation des dons familiaux ;
suppression de la CFE et des impôts de production (non chiffré).

**Dépenses publiques.** Économies sur l'immigration (15 Md€ en 2027, 29 Md€ en année pleine), réorganisation de l'État
(20,7 Md€ dès 2027, avec centralisation des recettes de TVA et transferts votés par le Parlement aux collectivités et à
la Sécurité sociale), contribution des collectivités (8,2 Md€, dont suppression des EPCI et des métropoles), agences
de l'État (3,4 Md€ ; une commission sénatoriale évaluait ces économies à environ 0,5 Md€), baisse de la contribution
au budget de l'Union (9 Md€).

**Protection sociale et retraites.** Âge légal ramené à 62 ans, 60 ans pour les carrières commencées avant 20 ans,
42 annuités, application au 1er janvier 2028, coût brut de 18,6 Md€ en 2032 selon le RN ; « pilier de capitalisation »
obligatoire, dont le Fonds de réserve pour les retraites serait le socle ; 15 à 20 Md€ d'économies « à terme » par la
« correction de mesures injustes » (non détaillées).

**Emploi, salaires, jeunesse, familles.** Permis de conduire gratuit (700 000 jeunes par an, 0,7 Md€), prime d'activité
étudiante (0,6 Md€), suppression de la CVEC, prêt à taux zéro au troisième enfant.

**Entreprises, industrie, énergie, commerce, souveraineté.** Suppression de la CFE et allègement des impôts de
production ; prix national régulé de l'électricité calculé sur les coûts de production français ; neutralité carbone
« avant 2050 » ; priorité nationale dans l'accès au logement, à l'emploi et aux prestations.

**Politique budgétaire et financement.** Le budget est présenté comme « réversible » ; la trajectoire repose sur des
économies dont une partie seulement est ventilée.

**Bénéficiaires et perdants potentiels (premier ordre).** Bénéficiaires : consommateurs d'énergie (davantage, en
montant, les ménages aisés qui consomment plus d'énergie, selon plusieurs analyses de presse), jeunes actifs,
familles, retraités ayant commencé à travailler tôt, entreprises redevables des impôts de production. Contributeurs :
étrangers (prestations et services publics, selon des modalités non publiées), collectivités territoriales et leurs
agents, opérateurs de l'État, budget européen.

**Traduction dans le modèle.** Hypothèses principales :

- économies « immigration » (15 Md€ en 2027) traduites en baisse de prestations [H] ; la part fondée sur la nationalité
  est incompatible avec le droit de l'Union pour les ressortissants européens, mais cette part n'est pas connue : la
  mesure est conservée et le risque signalé ;
- « réorganisation de l'État » (20,7 Md€) traduite en baisse de consommation publique ; les contributions des
  collectivités (8,2 Md€) et des agences (3,4 Md€) sont traitées comme des composantes de cette enveloppe et ne sont
  pas additionnées [H, faute de précision dans les sources] ;
- TVA sur l'énergie traduite en baisse équivalente du taux normal (le modèle ne distingue pas l'énergie) pour un coût
  de 10 Md€ [tiers, H] ;
- réforme des retraites simulée par M9 : 62 ans, 168 trimestres, départ à 60 ans pour 17 % de chaque génération (part
  des départs pour carrière longue au régime général) [H] ;
- économies sur les retraites (15-20 Md€) et pilier de capitalisation : non simulés faute de mesures identifiées.


**Tableau : mesures du corpus — Le Pen (RN).** Montants en Md€ (signe du point de vue du solde public), année de référence entre parenthèses ; « début » : première année d'application dans le modèle ; UE : niveau de qualification (chapitre \ref{sec:europe}).

| id | mesure | montant | chiffrage | début | traduction dans le modèle | quant. | UE |
|---|---|---|---|---|---|---|---|
| P01 | 140 Md€ d'économies nettes d'ici 2032 ; dette de 121 % (2027) à 112 % (2032) ; déficit à 3 % en 2030 ; 30 Md€ de baisses d'impôts | +140,0 (2032) | candidat | 2027 | régime (objectif) | non | — |
| P02 | Règle d'or constitutionnelle par référendum (déficit plafonné au niveau stabilisant la dette) | — | candidat | 2027 | régime (R1_actif) | non | 0 |
| P03 | Économies sur le « coût de l'immigration » | +15,0 (2027) | candidat | 2027 | `transferts_menages` −15,0 Md€ | partiel | 4 |
| P04 | Baisse de la contribution au budget de l'Union | +9,0 (2027) | candidat | 2027 | `recettes_neutres` +9,00 | oui | 2 |
| P05 | Réorganisation de l'État (centralisation de la TVA, transferts aux collectivités et à la Sécurité sociale votés par le Parlement) | +20,7 (2027) | candidat | 2027 | `autres_depenses` −20,70 | partiel | — |
| P06 | Contribution des collectivités (dont suppression des EPCI et métropoles 0,25 Md€, effectifs 0,8 Md€) | +8,2 (2027) | candidat | 2027 | — | partiel | — |
| P07 | Agences de l'État | +3,4 (2027) | candidat | 2027 | — | partiel | — |
| P08 | Âge légal ramené à 62 ans (60 ans pour les carrières commencées avant 20 ans), 42 annuités ; pilier de capitalisation obligatoire (socle : Fonds de réserve pour les retraites) | −18,6 (2032) | candidat | 2028 | `retraites` : age=62, mode=immediat, duree=168, groupe=60, groupe_part=0,17 | partiel | — |
| P09 | Économies sur les retraites (« corrections de mesures injustes ») | +17,5 (2032) | candidat | 2027 | — | partiel | — |
| P10 | TVA ramenée de 20 % à 5,5 % sur l'électricité, le gaz, le fioul et les carburants | −10,0 (2022) | tiers | 2027 | `tva` −1,22 | partiel | 2 |
| P11 | Exonération d'impôt sur le revenu des moins de 30 ans (jusqu'à 4 SMIC) | −2,0 (2027) | candidat | 2027 | `transferts_menages` +2,0 Md€ | oui | — |
| P12 | Permis de conduire gratuit (18 ans, casier vierge) ; prime d'activité étudiante | −1,3 (2027) | candidat | 2027 | `transferts_menages` +1,3 Md€ | oui | — |
| P13 | Part fiscale pleine dès le deuxième enfant | −3,5 (2027) | candidat | 2027 | `transferts_menages` +3,5 Md€ | oui | — |
| P14 | Dons familiaux défiscalisés ; prêt à taux zéro au troisième enfant ; suppression de la CVEC | — | aucun | 2027 | — | partiel | — |
| P15 | Suppression de la CFE et des impôts de production « qui nuisent à la relocalisation » | — | aucun | 2027 | `impots_production` (montant à préciser) | partiel | 0 |
| P16 | Priorité nationale (logement, emploi, prestations) | — | aucun | 2027 | — | non | 4 |

## Édouard Philippe (Horizons) {#sec:prog-horizons}

**Vision économique et sociale.** Le programme se présente comme « massif », « sérieux » et « en rupture » avec la
décennie écoulée : réduction de la dépense publique (« l'argent magique n'existe pas »), allongement de la durée du
travail (retraite à 65 ans, fin des 35 heures), réforme de l'État (250 000 postes en moins, statut limité au régalien
et à l'enseignement), soutien à la compétitivité (baisse de 50 Md€ des impôts de production) et à la natalité, moratoire
fiscal et normatif. Un « volume 2 » est annoncé pour janvier 2027.

**Principaux objectifs chiffrés.** Près de 150 Md€ d'économies pour ramener le déficit sous 2,5 % du PIB à la fin du
quinquennat (le chiffre de 2 % circule également dans la presse) ; la moitié de l'effort sur les dépenses sociales, un
quart sur l'État et les collectivités, un quart « sur la croissance » ; règle d'or adoptée par référendum dès le début
du quinquennat ; aucun nouvel impôt pendant cinq ans.

**Mesures fiscales.** Baisse de 50 Md€ des impôts de production financée par 50 Md€ de baisse des aides aux
entreprises (« pacte » pluriannuel, dès la première loi de finances) ; heures supplémentaires défiscalisées et deux
heures hebdomadaires exonérées de cotisations ; exonération d'impôt sur le revenu pendant les trois premières années
de l'enfant pour les classes moyennes ; suppression des frais de notaire pour le premier achat avant 35 ans.

**Dépenses publiques.** 250 000 postes de fonctionnaires en moins sur le quinquennat (un départ sur trois non remplacé
dans les fonctions de bureau) ; hausse de 20 % du salaire des enseignants ; fusion, suppression ou privatisation d'une
trentaine d'agences et d'opérateurs (dont France Travail) ; fonds d'adaptation climatique de 2 Md€ par an.

**Protection sociale et retraites.** Retraite à 65 ans et 45 annuités, départ précoce pour un tiers des assurés,
capitalisation collective ; indemnisation chômage limitée à 12 mois pour les moins de 50 ans ; baisse de 30 % du
nombre d'allocataires du RSA ; trois jours de carence pour tous ; allocation familiale unique de 350 € par mois dès le
premier enfant, dégressive.

**Emploi et salaires ; énergie ; commerce.** Fin des 35 heures ; relance du nucléaire (14 réacteurs) ; suppression du
« zéro artificialisation nette ».

**Bénéficiaires et perdants potentiels (premier ordre).** Bénéficiaires : entreprises redevables des impôts de
production (au détriment de celles qui bénéficient des aides supprimées), salariés effectuant des heures
supplémentaires, familles avec enfants, enseignants, primo-accédants jeunes. Contributeurs : générations nées après
le milieu des années 1960 (âge et durée), demandeurs d'emploi de moins de 50 ans, allocataires du RSA, agents publics
(effectifs), bénéficiaires des aides aux entreprises supprimées.

**Traduction dans le modèle.** Peu de mesures sont chiffrées une à une ; la lecture par objectifs budgétaires (lecture
B) est donc essentielle. Hypothèses principales :

- 250 000 postes en moins atteints en cinq ans (coût moyen de 56 000 € par agent du simulateur) ;
- retraites : 65 ans et 180 trimestres, un trimestre par génération, un tiers des assurés aux conditions actuelles
  [H] ;
- fin des 35 heures : durée de référence portée à 37 heures (deux heures supplémentaires annoncées) [H] ;
- RSA : baisse de 30 % du montant forfaitaire comme approximation budgétaire d'une baisse des effectifs [H] ;
- pacte impôts de production / aides : moitié des aides assimilée à des subventions (effet net nul dans le modèle),
  moitié à des allègements de cotisations (hausse du coût du travail) [H], avec deux variantes ; le modèle ne distingue
  pas les distorsions propres aux impôts de production de celles des subventions, argument central du candidat ;
- non simulés faute de barème : allocations familiales, assurance chômage (montant), jours de carence, mesures
  familiales.


**Tableau : mesures du corpus — Philippe (Horizons).** Montants en Md€ (signe du point de vue du solde public), année de référence entre parenthèses ; « début » : première année d'application dans le modèle ; UE : niveau de qualification (chapitre \ref{sec:europe}).

| id | mesure | montant | chiffrage | début | traduction dans le modèle | quant. | UE |
|---|---|---|---|---|---|---|---|
| H01 | Près de 150 Md€ d'économies ; déficit sous 2,5 % du PIB en fin de quinquennat ; moitié de l'effort sur les dépenses sociales, un quart sur l'État et les collectivités, un quart sur la croissance | +150,0 (2032) | candidat | 2027 | régime (objectif) | non | — |
| H02 | Règle d'or constitutionnelle par référendum ; aucun nouvel impôt pendant cinq ans | — | candidat | 2027 | régime (R2_actif_depenses) | non | 0 |
| H03 | 250 000 postes de fonctionnaires en moins (un départ sur trois non remplacé dans les fonctions de bureau) | — | aucun | 2027 | `emploi_public` −250,00 | oui | — |
| H04 | Hausse de 20 % du salaire des enseignants | — | aucun | 2027 | — | partiel | — |
| H05 | Âge de départ à 65 ans et 45 annuités ; départ précoce pour un tiers des assurés ; capitalisation collective | — | aucun | 2028 | `retraites` : age=65, mode=progressif, duree=180, duree_mode=progressif, groupe=ref, groupe_part=0,33 | partiel | — |
| H06 | Fin des 35 heures ; deux heures supplémentaires hebdomadaires exonérées de cotisations | — | aucun | 2027 | `temps_travail` +37,00 | partiel | — |
| H07 | Indemnisation limitée à 12 mois pour les moins de 50 ans | — | aucun | 2027 | `assurance_chomage` (montant à préciser) | partiel | — |
| H08 | Baisse de 30 % du nombre d'allocataires du RSA (accompagnement, métiers en tension) | — | aucun | 2027 | `rsa` −30,00 | partiel | — |
| H09 | Trois jours de carence pour tous (public et privé) | — | aucun | 2027 | — | non | — |
| H10 | Allocation de 350 € par mois dès le premier enfant, dégressive ; exonération d'impôt les trois premières années de l'enfant ; suppression des frais de notaire au premier achat (< 35 ans) ; prêt à taux zéro famille | — | aucun | 2027 | — | partiel | — |
| H11 | Baisse de 50 Md€ des impôts de production financée par 50 Md€ de baisse des aides aux entreprises | +0,0 (2028) | candidat | 2028 | `impots_production` −25,00; `cotisations_employeurs` +25,00 | partiel | 0 |
| H12 | Fonds unique d'adaptation au changement climatique | −2,0 (2027) | candidat | 2027 | `investissement_public` +2,00 | oui | — |
| H13 | Fusion, suppression ou privatisation d'une trentaine d'agences (dont France Travail) | — | aucun | 2027 | — | partiel | — |
| H14 | Huit réacteurs nucléaires supplémentaires ; suppression du ZAN | — | aucun | 2027 | — | non | — |

## Éléments de régime : règles d'or et objectifs de solde {#sec:prog-regimes}

Les trois candidats annoncent des objectifs de finances publiques qui ne sont pas des mesures mais des **règles** :
stabilisation de la dette en un quinquennat (LFI), déficit à 3 % en 2030 et règle d'or par référendum (RN), déficit
sous 2,5 % en fin de quinquennat et règle d'or (Horizons). Le modèle les représente dans la lecture B par une
trajectoire cible du solde public, atteinte par un effort réparti selon les priorités déclarées :

| Candidat | Objectif annoncé | Cible du modèle | Instruments de l'effort non ventilé [H] |
|---|---|---|---|
| Mélenchon (LFI) | réduction du déficit de 24,7 Md€ en 2027 (mesures) puis stabilisation du ratio dette/PIB en un quinquennat | solde stabilisant la dette en 2032 (calculé dans le modèle) | impots menages 100 % |
| Le Pen (RN) | déficit à 3 % du PIB en 2030 ; dette de 121 % (2027) à 112 % (2032) ; 140 Md€ d'économies | −3,0 % du PIB en 2030 | conso publique 60 %, prestations 40 % |
| Philippe (Horizons) | déficit sous 2,5 % du PIB en fin de quinquennat ; moitié de l'effort sur les dépenses sociales, un quart sur l'État et les collectivités, un quart « sur la croissance » ; aucun nouvel impôt | −2,5 % du PIB en 2032 | prestations 67 %, conso publique 33 % |

Ces compositions sont des lectures prudentes des déclarations, non des engagements : LFI annonce un financement par
des recettes nouvelles (d'où les impôts des ménages, sans pouvoir cibler les hauts revenus dans ce canal agrégé) ; le
RN des économies sur l'État, les collectivités, l'immigration et les retraites ; Horizons la moitié de l'effort sur les
dépenses sociales et un quart sur l'État et les collectivités, sans hausse d'impôt (le quart « croissance » n'est pas
un instrument : il est laissé au modèle).

## Degré d'incertitude des programmes {#sec:incertitude-programmes}

L'incertitude sur les programmes eux-mêmes est de trois ordres :

1. **Incertitude de contenu** : mesures non chiffrées, enveloppes non ventilées, barèmes non publiés (impôt sur le
   revenu à 14 tranches, allocation familiale de 350 €, durée d'indemnisation du chômage) ;
2. **Incertitude de chiffrage** : rendements annoncés supérieurs aux rendements simulés (impôts sur le capital et les
   patrimoines), coûts sans chiffrage du candidat (TVA sur l'énergie), estimations contestées (économies sur les
   agences de l'État) ;
3. **Incertitude d'exécution** : calendrier parlementaire, contentieux constitutionnels et européens, réactions des
   acteurs (chapitre \ref{sec:europe}).

Le programme de LFI est le mieux documenté pour 2027 mais ne l'est pas au-delà ; ceux du RN et d'Horizons fixent des
trajectoires de moyen terme mais ventilent peu leurs économies. Aucun des trois n'est donc « complètement » simulable :
la comparaison doit respecter ces différences de précision (chapitre \ref{sec:resultats}).
