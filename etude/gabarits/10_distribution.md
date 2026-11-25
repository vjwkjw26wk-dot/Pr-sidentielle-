# Distribution des effets économiques et sociaux {#sec:distribution}

Ce chapitre examine qui gagne et qui perd, au moins au premier ordre. Il distingue trois niveaux, de précision
décroissante : les **effets statiques** des mesures socio-fiscales, calculés ménage par ménage par la
microsimulation ; les **effets générationnels moyens** des réformes des retraites, calculés par génération et par sexe
par le module M9 ; et les **effets macroéconomiques moyens** (emploi, salaires, prix), qui ne sont pas répartis entre
ménages dans cette étude et ne peuvent être commentés que qualitativement.

## Effets moyens et effets individuels {#sec:moyens-individuels}

Un effet moyen par décile peut masquer des situations individuelles très diverses : au sein d'un même décile,
certains ménages gagnent et d'autres perdent selon leur composition familiale, leur statut d'activité, leur logement
ou leurs revenus du capital. Les tableaux donnent donc, pour chaque décile, la part de gagnants et de perdants
(ménages dont le revenu disponible varie de plus d'un euro par an). Par ailleurs, l'effet statique ne tient compte ni
des changements de comportement (offre de travail, optimisation fiscale), ni des effets macroéconomiques induits
(emploi, salaires, prix), qui peuvent être du même ordre de grandeur que l'effet direct pour certaines catégories.

## Effets statiques par décile de niveau de vie {#sec:deciles}

**Couverture.** Seules les mesures dont l'incidence ménage par ménage est représentée entrent dans ces tableaux :
barèmes et prestations calculés par OpenFisca (RSA, prime d'activité, allocations familiales, aides au logement, impôt
sur le revenu, CSG) et mesures réparties selon des profils (TVA selon la structure de consommation par quintile, impôts
sur le capital sur le haut de la distribution). Les mesures traitées en transferts non ciblés, en recettes sans canal
propre ou en dépenses publiques n'y figurent pas ; les réformes des retraites sont traitées à la section suivante.

{{inc:t10_deciles}}

**Lecture.** Pour LFI, les mesures représentées (imposition du capital et des patrimoines) pèsent sur le haut de la
distribution ; les transferts (garantie d'autonomie, revalorisations) et la hausse du SMIC, qui bénéficieraient au
bas et au milieu de la distribution, ne sont pas répartis par la microsimulation dans cette version (transferts non
ciblés, SMIC traité par le canal salarial). Pour le RN, la baisse de la TVA sur l'énergie, répartie selon la structure de
consommation, bénéficie à tous les déciles, un peu plus en proportion du revenu aux ménages modestes et davantage en
euros aux ménages aisés ; les économies sur l'immigration, traitées en transferts non ciblés, n'y sont pas réparties.
Pour Horizons, la baisse du RSA concentre les pertes sur les premiers déciles.

## Actifs, retraités, jeunes et générations {#sec:generations}

Les réformes des retraites ont des effets très différenciés selon les générations : elles ne concernent pas les
retraités actuels, ni les générations qui atteignent l'âge légal avant leur entrée en vigueur ; elles modifient l'âge
de départ, la durée de retraite et le niveau de pension des générations suivantes.

{{inc:t10_generations}}

**Lecture.** Les écarts d'âge pivot mesurent le décalage moyen de la cessation d'activité d'une génération ;
l'écart de durée de retraite attendue en est approximativement l'opposé (à espérance de vie inchangée). Pour LFI et le
RN, les générations nées à partir du milieu des années 1960 partiraient en moyenne plus tôt (jusqu'à deux ans environ,
davantage pour les carrières longues dans la réforme du RN) ; pour Horizons, les générations nées après 1970 partiraient
en moyenne plus d'un an plus tard (davantage pour les hommes, dont le report en réponse à la durée requise est plus
élevé dans la littérature), avec un niveau de pension légèrement réduit pour la fraction qui ne reporte pas son départ.
Le financement de ces réformes concerne, lui, toutes les générations (cotisations, impôts, dette) ; sa répartition
dépend des choix budgétaires (lecture B) et de la dynamique de la dette, qui reporte une partie de la charge sur les
générations futures.

## Catégories socioprofessionnelles, entreprises, secteurs et territoires {#sec:categories}

La microsimulation ne distingue pas les catégories socioprofessionnelles de manière fiable (score latent construit à
partir des grilles de salaires) ; les effets par catégorie ne sont donc pas publiés. Le modèle macroéconomique distingue
25 branches marchandes : les effets sectoriels (industrie, services, construction) sont disponibles dans les sorties
détaillées mais ne sont pas commentés ici, faute de validation suffisante des équations de branche à cet horizon. Les
entreprises ne sont pas distinguées par taille (la baisse des impôts de production et la suppression des aides
concernent pourtant des entreprises différentes : la CVAE et la C3S pèsent surtout sur les grandes entreprises, la
CFE sur toutes). Les effets territoriaux ne sont pas représentés.

Qualitativement, les mesures étudiées ont des incidences sectorielles et territoriales connues : les hausses du SMIC
et du point d'indice concernent davantage les territoires où la part de l'emploi public et des bas salaires est élevée ;
la suppression d'emplois publics et la réorganisation des collectivités (RN, Horizons) concernent davantage les
territoires peu denses ; la baisse des impôts de production bénéficie d'abord à l'industrie.

## Limites de la microsimulation {#sec:limites-micro}

1. **Échantillon** : 2 % des ménages pour l'impôt, deux sous-échantillons de 0,5 % pour les prestations ; erreur
   d'échantillonnage de l'ordre de 2 % sur les montants.
2. **Revenus de 2024**, non revalorisés avec les salaires, l'emploi et les prix simulés (pas de retour macro → micro).
3. **Patrimoine** : approché par les revenus du patrimoine ; les ménages à patrimoine peu productif de revenu imposable
   sont sous-représentés, d'où une répartition approximative des impôts sur le patrimoine.
4. **Non-recours** : supposé constant (taux de recours apparent de 2024) ; une hausse des prestations peut modifier le
   recours.
5. **Catégories mal représentées** : très hauts revenus et patrimoines (agrégats), indépendants, ménages complexes,
   personnes hors ménages ordinaires (institutions).
6. **Comportements** : l'offre de travail réagit en moyenne (M15) ; les réactions individuelles (seuils, effets de
   palier) ne sont pas microsimulées.
