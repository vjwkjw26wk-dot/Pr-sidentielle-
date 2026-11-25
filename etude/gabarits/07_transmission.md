# Transmission macroéconomique des mesures {#sec:transmission}

Ce chapitre explique comment chaque grande famille de mesures agit sur l'économie dans le modèle, en distinguant les
effets de demande (rapides), les effets d'offre (lents), les effets de financement et de dette, et l'incidence des
prélèvements. Il s'appuie sur des chocs standardisés simulés pour l'occasion (section \ref{sec:multiplicateurs}), qui
servent de clé de lecture aux résultats des programmes (chapitre \ref{sec:resultats}).

## Effets de demande à court terme {#sec:demande-ct}

Une mesure qui augmente le revenu des ménages ou la dépense publique augmente la demande adressée aux entreprises. Le
premier tour dépend de la nature de la mesure :

- **dépense publique** (consommation, investissement) : elle entre directement dans la demande finale ; une partie est
  importée (selon les contenus en importations du TES) ;
- **transferts et baisses d'impôts des ménages** : seule la part consommée entre dans la demande (85 % la première
  année en moyenne, plus pour les ménages modestes, moins pour les ménages aisés) ;
- **baisses d'impôts sur les entreprises** : elles passent par les prix (répercussion), les salaires (incidence) et
  les marges ; l'effet de demande est indirect et plus lent.

Les tours suivants passent par la production, l'emploi, les revenus et la consommation : c'est le multiplicateur
keynésien. Les fuites sont les importations, l'épargne et les prélèvements obligatoires.

## Effets d'offre à moyen et long terme {#sec:offre-lt}

L'offre (le PIB potentiel) dépend de la population active, du chômage structurel, du capital et de la productivité.
Dans le modèle, les mesures agissent sur l'offre par cinq canaux :

1. **Population active** : âge de la retraite et durée d'assurance (M9), incitations au travail des prestations
   (M15) ;
2. **Chômage structurel** : générosité de l'assurance chômage, formation ;
3. **Capital** : investissement des entreprises (accélérateur, coût d'usage), capital public ;
4. **Productivité** : capital public, R&D (exploratoire), durée du travail (productivité horaire) ;
5. **Coût relatif des facteurs** : cotisations, impôts de production, salaires (substitution capital-travail, $\sigma$).

La fermeture d'offre ramène progressivement la demande vers ce potentiel : un programme qui accroît le potentiel
(davantage d'actifs, de capital) a des effets positifs croissants dans le temps, et inversement.

## Multiplicateurs budgétaires simulés {#sec:multiplicateurs}

Le tableau suivant donne les effets de chocs permanents d'environ 0,5 point de PIB, appliqués à partir de 2028, sous
le régime principal (taux exogènes, règle figée) et sous le régime avec réaction de la BCE et prime souveraine. Le
multiplicateur est le rapport entre la variation du PIB et le coût ex ante du choc (en part du PIB).

{MULT}

Lecture : {MULT_LECTURE}

Ces valeurs sont à comparer aux estimations empiriques (chapitre \ref{sec:theorie}) : les multiplicateurs de dépense de
première année du modèle se situent dans le haut de la fourchette (0,6-1,2 pour la plupart des estimations, davantage
en récession), parce que les taux sont exogènes dans le régime principal et que la fermeture est lente. Sous le régime
BCE + prime, la hausse des taux réduit légèrement l'effet ; avec une fermeture rapide ($\rho = 0{,}3$), il s'estompe
plus vite (chapitre \ref{sec:robustesse}).

## Effets de financement et de dette {#sec:financement}

Une mesure non financée augmente la dette ; la charge d'intérêts correspondante dépend du taux de marché auquel la
dette nouvelle est émise et de la vitesse de renouvellement (cohortes, M17). Avec un taux de 4,89 % et une croissance
nominale de 2 à 3 %, chaque point de PIB de déficit supplémentaire et permanent alourdit la dette de façon
cumulative : l'effet sur le ratio de dette à 20 ans est de l'ordre de 20 points pour un déficit permanent de 1 point,
avant effets d'activité. Inversement, une mesure qui améliore le solde ne réduit le ratio de dette qu'après avoir
compensé l'effet de la baisse d'activité sur le dénominateur (encadré 1.1).

Dans le régime BCE + prime, une dégradation du solde et de la dette augmente l'écart OAT-Bund (1,3 point de base par
point de dette hors crise, jusqu'à 11,8 points de base par point de déficit avec la crise), ce qui renchérit le crédit
aux ménages et aux entreprises et amplifie la dynamique de la dette.

## Incidence fiscale sur ménages, salariés et entreprises {#sec:incidence}

L'incidence d'un prélèvement — qui le supporte réellement — diffère de son redevable légal.

| Prélèvement | Hypothèse du modèle | Source, statut |
|---|---|---|
| TVA, taux normal | répercussion de 95 % des hausses, 50 % des baisses sur les prix à la consommation | Benzarti et al. (2020) [B] |
| Taux réduits de TVA | répercussion 50 % (hausses), 25 % (baisses) | idem, extrapolé [C] |
| Cotisations employeurs | transmission de 50 % aux salaires à long terme ; le reste sur le coût du travail | Bozio, Breda et Grenet (2019) ; Carbonnier et al. (2019) [C] |
| Impôts de production | 50 % répercutés sur les prix de la valeur ajoutée, 20 % sur les salaires, 30 % sur les marges | CAE (2019), hypothèse [D] |
| Impôt sur les sociétés | 30 % supportés par les salariés à long terme ; semi-élasticité des bénéfices déclarés 0,8 (transfert de bénéfices des groupes, la moitié de l'IS) | Fuest, Peichl et Siegloch (2018) ; méta-analyses [C/B] |
| Impôts sur le capital des ménages (PFU, ISF, successions) | érosion d'assiette selon M13 (fourchette basse, centrale, haute) ; pas d'effet sur l'investissement des entreprises | littérature [C] |

**Exemple chiffré : rendement annoncé et rendement simulé.** Pour la suppression du prélèvement forfaitaire unique
(9 Md€ annoncés), le module M13 donne un rendement net de 5,3 Md€ en valeur centrale (7,5 Md€ et 1,6 Md€ dans les
hypothèses basse et haute de réaction), du fait de la baisse des dividendes distribués ; pour l'impôt sur la fortune
(10 Md€ annoncés), 7,1 Md€ (8,8 et 5,0) ; pour les successions (20 Md€), 18 Md€ (20 et 15). Ces écarts ne mesurent pas
la « sincérité » d'un chiffrage : ils traduisent l'incertitude sur les comportements des contribuables les plus
mobiles.

## Effets sur le coût du capital et l'investissement {#sec:cout-capital}

L'investissement des entreprises réagit d'abord à la demande (accélérateur), puis au coût d'usage du capital (taux du
crédit, impôt sur les sociétés, prix de l'investissement) et à la trésorerie. Une hausse de l'impôt sur les sociétés
réduit l'investissement par le coût d'usage (élasticité −0,18, fragile) et par la trésorerie (0,10) ; une baisse des
impôts de production l'augmente surtout par la demande induite et la marge. Le modèle n'a pas d'effet de l'incertitude
sur l'investissement, ni d'effet spécifique des impôts de production sur la localisation des activités : ces deux
canaux, invoqués respectivement contre les programmes jugés risqués et en faveur de la baisse des impôts de production,
ne sont donc pas représentés (chapitre \ref{sec:comportements}).

## Investissement public et privé {#sec:invest-pub-priv}

L'investissement public a un effet de demande (comme toute dépense) et un effet d'offre par le capital public
(élasticité de 0,08) ; l'investissement hors administrations (pôle public bancaire) n'a, dans le modèle, que l'effet
de demande, sans effet d'offre ni effet d'éviction par le crédit : c'est une borne haute de son effet, qui suppose que
les projets financés sont additionnels (ils n'auraient pas été réalisés sans le pôle public) et que leur financement
n'évince pas d'autres crédits.

## Productivité et innovation {#sec:productivite}

La productivité tendancielle étant exogène, le modèle ne représente pas les effets de long terme de l'éducation, de la
qualité des services publics, de l'organisation de l'État, de l'intelligence artificielle (invoquée par Horizons pour
le non-remplacement des agents) ou de la concurrence. Deux mesures modifient la productivité dans le modèle : la durée
du travail (productivité horaire) et l'investissement public (capital public). C'est une limite importante pour les
programmes qui revendiquent des gains de productivité de long terme.

## Marché du travail {#sec:travail-transmission}

L'emploi réagit à la production (à court terme, élasticité de 0,26 puis convergence) et au coût relatif du travail
($\sigma$). Le chômage dépend en plus de la population active : une réforme qui augmente le nombre d'actifs (report de
l'âge de la retraite) augmente d'abord le chômage, tant que la demande de travail ne s'est pas ajustée, puis la
fermeture d'offre absorbe progressivement ces actifs supplémentaires ; une réforme qui réduit le nombre d'actifs
(abaissement de l'âge) réduit d'abord le chômage puis l'emploi. Les hausses du SMIC et du point d'indice augmentent le
coût du travail et les revenus : l'effet net sur l'emploi dépend de l'élasticité de substitution et de l'effet de
demande.

## Inflation et pouvoir d'achat {#sec:inflation-pa}

Le pouvoir d'achat (revenu disponible réel) dépend des revenus nominaux (salaires, emploi, prestations, impôts) et des
prix. Une hausse de salaires augmente le pouvoir d'achat à court terme, mais se diffuse aux prix (transmission du coût
salarial unitaire aux prix de la valeur ajoutée, puis prix de Leontief) ; une baisse de TVA le relève par les prix,
partiellement (répercussion de 50 % pour une baisse). Les mesures d'économie sur les prestations le réduisent
directement.

## Compétitivité et commerce extérieur {#sec:competitivite}

La compétitivité-prix dépend des prix à l'exportation, eux-mêmes déterminés par les coûts (salaires, impôts de
production, consommations intermédiaires). Les mesures qui augmentent les coûts (SMIC, point d'indice indirectement,
cotisations) détériorent les exportations (élasticité-prix −0,60) ; celles qui les réduisent (impôts de production,
cotisations) les améliorent. Les relances de la demande augmentent les importations (élasticité de 1,47 à court
terme), ce qui dégrade le solde extérieur.

## Anticipations et comportements {#sec:anticipations-transmission}

Les anticipations du modèle sont adaptatives ; les annonces n'ont pas d'effet avant leur mise en œuvre. Le modèle ne
représente pas : les effets de confiance (positifs ou négatifs) d'une alternance politique ; les réactions des
marchés financiers au-delà de la prime estimée et des chocs de scénario ; l'attentisme des entreprises face à
l'incertitude réglementaire ; les comportements d'anticipation des ménages (achats avant une hausse de TVA, départs à
la retraite avant une réforme). Le chapitre \ref{sec:comportements} discute ces limites.

## Mécanismes contradictoires {#sec:contradictoires}

Une même mesure peut produire des effets de sens opposés selon l'horizon et le canal. Exemples tirés des programmes :

| Mesure | Effet favorable | Effet défavorable |
|---|---|---|
| Hausse du point d'indice (+10 %) | demande (revenus des agents), pouvoir d'achat | coût budgétaire, diffusion aux salaires privés et aux prix, compétitivité |
| Abaissement de l'âge de la retraite | revenus des seniors, chômage plus faible à court terme | population active et potentiel plus faibles, pensions plus élevées, dette |
| Report de l'âge et allongement de la durée | potentiel, finances publiques à long terme | chômage des seniors à court terme, pensions plus faibles pour qui ne reporte pas |
| Baisse de TVA sur l'énergie | prix et pouvoir d'achat | coût budgétaire, avantage proportionnellement plus élevé en euros pour les gros consommateurs, signal-prix carbone |
| Baisse de la dépense publique et des prestations | solde public, dette à moyen terme | demande, emploi, revenus des ménages modestes ; ratio de dette à court terme |
| Hausse de l'imposition du capital | recettes, redistribution | érosion d'assiette, éventuels départs, épargne et dividendes |
| Baisse des impôts de production contre baisse des aides | baisse des coûts de production, prix, marges | perte des bénéficiaires des aides ; effet net nul si les aides étaient des subventions équivalentes |
