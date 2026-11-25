# Résultats des simulations comparatives {#sec:resultats}

Ce chapitre présente les résultats disponibles pour chaque programme et chaque scénario. Il respecte quatre règles :
(i) tous les chiffres proviennent des simulations archivées (`phase7/resultats`), générés automatiquement dans les
tableaux ; (ii) les résultats de la **lecture A** (mesures documentées) et de la **lecture B** (objectifs budgétaires)
sont présentés séparément et ne doivent pas être confondus ; (iii) les horizons de 5 et 10 ans sont les horizons
principaux, celui de 20 ans est conditionnel à des hypothèses de long terme fortes ; (iv) les simulations non exécutées
sont signalées comme telles.

## Lire les résultats {#sec:lire}

Tous les effets sont des **écarts à une trajectoire de référence** sans le programme, simulée dans le même
environnement et sous le même régime : un PIB à « +1 % » à cinq ans signifie que le PIB de 2031 est supérieur de 1 % à
ce qu'il serait sans le programme, pas que la croissance de 2031 est de 1 %. Les niveaux de solde et de dette sont
donnés séparément, car la référence elle-même se dégrade fortement (chapitre \ref{sec:donnees}) : avec l'OAT à 4,89 %,
la dette de référence atteint environ 133 % du PIB en 2031, 156 % en 2036 et 225 % en 2046 sous la règle R2 figée.

Trois avertissements spécifiques s'imposent avant toute lecture.

1. **Les ordres de grandeur du chômage ne sont pas fiables pour les grands programmes.** Le chômage du modèle est la
   différence entre une population active en partie exogène et un emploi déterminé par la production ; les réformes qui
   modifient fortement la population active (âge de la retraite) ou la demande produisent des écarts de chômage
   beaucoup plus amples que ce que suggérerait la loi d'Okun. Les signes sont informatifs, les niveaux beaucoup moins
   (chapitre \ref{sec:robustesse}).
2. **La lecture B mesure l'ampleur d'un effort, pas une trajectoire probable.** Comme la référence dérive (effet boule
   de neige), atteindre un déficit de 2,5 ou 3 % du PIB exige un effort croissant, que le modèle traduit en
   consolidation budgétaire à multiplicateurs élevés. Les effets récessifs qui en résultent sont des ordres de grandeur
   conditionnels à la référence et à l'hypothèse de taux.
3. **Les recettes sans canal propre ont été traitées sans effet sur la demande** (taxes sur les très grands patrimoines,
   les multinationales, les transactions financières, la fraude ; économies sur la contribution européenne) : leurs
   montants sont des bornes hautes de rendement et leurs effets macroéconomiques indirects ne sont pas représentés.

## Lecture A : mesures documentées {#sec:lecture-a}

**Tableau : lecture A (mesures documentées), principaux indicateurs.** Écarts à la référence du même environnement et du même régime (R2 figé, taux exogènes) ; horizons 2031, 2036, 2046. Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — indicateur | 5 ans | 10 ans | 20 ans |
|---|---|---|---|
| Mélenchon (LFI) — PIB (%) | +1,8 | −0,5 | −1,1 |
| Mélenchon (LFI) — emploi (milliers) | +606,6 | −48,8 | −539,3 |
| Mélenchon (LFI) — chômage (pt) | −4,5 | −2,8 | −1,4 |
| Mélenchon (LFI) — pouvoir d'achat (%) | +3,4 | +4,3 | +5,3 |
| Mélenchon (LFI) — solde (pt PIB) | +3,3 | +3,7 | +5,6 |
| Mélenchon (LFI) — dette (pt PIB) | −20,1 | −38,1 | −73,6 |
| Le Pen (RN) — PIB (%) | −2,0 | −2,9 | −3,6 |
| Le Pen (RN) — emploi (milliers) | −440,3 | −754,3 | −1049,7 |
| Le Pen (RN) — chômage (pt) | −1,8 | −1,6 | −1,1 |
| Le Pen (RN) — pouvoir d'achat (%) | −0,9 | −0,6 | −0,0 |
| Le Pen (RN) — solde (pt PIB) | +0,3 | +0,0 | +0,2 |
| Le Pen (RN) — dette (pt PIB) | −0,3 | −1,6 | −3,3 |
| Philippe (Horizons) — PIB (%) | +1,0 | +2,4 | +4,1 |
| Philippe (Horizons) — emploi (milliers) | −622,4 | −267,5 | +255,9 |
| Philippe (Horizons) — chômage (pt) | +2,6 | +2,6 | +1,9 |
| Philippe (Horizons) — pouvoir d'achat (%) | −1,1 | −1,0 | −1,9 |
| Philippe (Horizons) — solde (pt PIB) | −0,6 | −0,5 | −0,7 |
| Philippe (Horizons) — dette (pt PIB) | +5,3 | +8,4 | +13,2 |

**Mélenchon (LFI).** Le paquet 2027 combine une relance (point d'indice, transferts, services publics, SMIC,
abaissement de l'âge de la retraite, investissement hors budget de 100 Md€ par an) et des hausses de prélèvements
concentrées sur le capital, les patrimoines et les grandes entreprises. À cinq ans, l'activité est supérieure à la
référence, le chômage nettement inférieur, les prix plus élevés (diffusion du SMIC, du point d'indice et de la
moindre offre de travail), et le solde public amélioré de plus de 3 points de PIB, ce qui réduit la dette d'une
vingtaine de points. Trois éléments expliquent l'essentiel de ces résultats : (a) les hausses de prélèvements, pour
environ 3 points de PIB, dont une large part est traitée sans effet sur la demande (hypothèse [H] la plus favorable au
programme) ; (b) l'investissement hors budget de 100 Md€ par an, qui ajoute de la demande sans coût budgétaire (borne
haute) ; (c) le retour à 62 ans, qui réduit la population active et le potentiel. Au-delà de cinq ans, la baisse de
l'offre de travail l'emporte : le PIB passe sous la référence à dix et vingt ans, l'emploi aussi, tandis que les prix
restent supérieurs.

**Le Pen (RN).** Les mesures documentées sont dominées par la réforme des retraites (62 ans, 42 annuités, carrières
longues à 60 ans), qui réduit la population active et le PIB potentiel de manière croissante : le PIB est inférieur à
la référence d'environ 2 % à cinq ans et 3,6 % à vingt ans, l'emploi d'environ 440 000 à 1 million. Les économies
identifiées (immigration, État, contribution européenne) et les baisses d'impôts (TVA sur l'énergie, jeunes, familles)
se compensent à peu près sur le solde ; la dette varie peu par rapport à la référence. Le pouvoir d'achat moyen baisse
légèrement à court terme (baisse des prestations ciblées par les économies « immigration », moindre emploi), malgré la
baisse de la TVA sur l'énergie.

**Philippe (Horizons).** Les mesures documentées sont celles qui augmentent l'offre (65 ans et 45 annuités, fin des
35 heures) et réduisent l'emploi public (250 000 postes), plus le pacte impôts de production / aides. Le PIB est
supérieur à la référence et croissant (de l'ordre de 1 % à cinq ans et 4 % à vingt ans) ; mais l'augmentation de la
population active et de la durée du travail précède celle de la demande de travail, d'où un chômage plus élevé à cinq et
dix ans, qui ne se résorbe que lentement. Le solde public se dégrade légèrement : les mesures documentées ne
contiennent pas l'essentiel des économies annoncées (près de 150 Md€), dont la composition n'est pas publiée ; c'est
précisément l'objet de la lecture B.

## Décomposition par mesure {#sec:decomposition}

Chaque mesure a été simulée isolément. Le tableau suivant donne les effets isolés, leur somme et l'écart entre la
somme et le paquet complet (« interactions »), qui provient des non-linéarités (prix, fermeture, plafonds).


**Tableau : effets des mesures isolées — Mélenchon (LFI)** (régime principal ; chaque mesure simulée seule). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| mesure | PIB 5 ans (%) | PIB 10 ans (%) | emploi 5 ans (k) | solde 5 ans (pt) | dette 10 ans (pt) |
|---|---|---|---|---|---|
| L01 Suppression du prélèvement forfaitaire unique (flat tax | −0,09 | −0,08 | −16,79 | +0,12 | −0,98 |
| L02 Rétablissement d'un impôt sur la fortune renforcé | −0,11 | −0,09 | −22,46 | +0,17 | −1,37 |
| L03 Taxe Zucman (patrimoines supérieurs à 100 M€) | +0,00 | +0,00 | +0,00 | +0,61 | −5,68 |
| L04 Réforme des droits de succession | +0,00 | +0,00 | +0,00 | +0,73 | −6,82 |
| L06 Rétablissement de la CVAE sur les plus grandes entrepri | −0,02 | −0,04 | +2,11 | +0,11 | −1,01 |
| L07 Réforme de l'impôt sur les sociétés | −0,04 | −0,07 | −3,40 | +0,05 | −0,29 |
| L08 Taxe universelle sur les multinationales | +0,00 | +0,00 | +0,00 | +0,20 | −1,89 |
| L09 Renforcement de la taxe sur les services numériques (GA | +0,00 | +0,00 | +0,00 | +0,16 | −1,48 |
| L10 Taxe sur les superprofits | +0,00 | +0,00 | +0,00 | +0,20 | −1,89 |
| L11 Rabot et suppression des niches fiscales et sociales «  | −0,39 | −0,25 | −109,99 | +0,46 | −4,37 |
| L13 Taxes sur les transactions financières | +0,00 | +0,00 | +0,00 | +0,20 | −1,89 |
| L14 Taxe sur les rachats d'actions | +0,00 | +0,00 | +0,00 | +0,10 | −0,95 |
| L15 Taxe sur les crypto-actifs | +0,00 | +0,00 | +0,00 | +0,04 | −0,38 |
| L16 Lutte contre la fraude fiscale | +0,00 | +0,00 | +0,00 | +0,08 | −0,76 |
| L20 Dégel et hausse de 10 % du point d'indice | +0,73 | +0,42 | +175,96 | −0,66 | +5,22 |
| L21 Revalorisation de 10 % des pensions, allocations famili | +0,11 | +0,04 | +30,94 | −0,16 | +1,44 |
| L22 Logements d'urgence et réquisition de logements vacants | +0,08 | +0,03 | +35,70 | −0,02 | −0,03 |
| L23 Garantie d'autonomie pour les jeunes | +0,14 | +0,05 | +36,71 | −0,19 | +1,68 |
| L24 SMIC à 1 700 € net | −0,00 | +0,02 | −39,31 | −0,16 | +0,70 |
| L26 10 000 postes dans l'Éducation nationale | +0,01 | +0,00 | +5,95 | −0,00 | −0,00 |
| L27 Gratuité de la cantine scolaire | +0,09 | +0,04 | +42,85 | −0,02 | −0,03 |
| L28 250 000 places à l'université | +0,09 | +0,03 | +41,66 | −0,02 | −0,03 |
| L29 Hôpital public (+10 000 postes soignants) | +0,08 | +0,03 | +35,70 | −0,02 | −0,03 |
| L30 Violences sexistes et sexuelles ; violences faites aux  | +0,12 | +0,05 | +54,75 | −0,02 | −0,04 |
| L31 Indexation des budgets 2027 des services supprimés en 2 | +0,18 | +0,07 | +83,30 | −0,04 | −0,06 |
| L32 Adaptation au dérèglement climatique | +0,26 | +0,39 | +6,55 | −0,32 | +3,14 |
| L33 Investissements de planification écologique portés par  | +1,70 | +0,65 | +427,99 | +1,21 | −12,75 |
| L34 Abrogation de la réforme de 2023 (retour à 62 ans) | −1,35 | −2,08 | −211,02 | +0,04 | −0,47 |
| L35 Abrogation des réformes de l'assurance chômage | +0,02 | −0,00 | +6,21 | −0,07 | +0,53 |
| Σ mesures isolées | +1,59 | −0,79 | +583,41 | +2,79 | −30,49 |
| paquet complet (A) | +1,84 | −0,54 | +606,60 | +3,32 | −38,14 |
| interactions (A − Σ) | +0,25 | +0,25 | +23,19 | +0,53 | −7,65 |

**Tableau : effets des mesures isolées — Le Pen (RN)** (régime principal ; chaque mesure simulée seule). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| mesure | PIB 5 ans (%) | PIB 10 ans (%) | emploi 5 ans (k) | solde 5 ans (pt) | dette 10 ans (pt) |
|---|---|---|---|---|---|
| P03 Économies sur le « coût de l'immigration » | −0,26 | −0,18 | −57,24 | +0,27 | −2,16 |
| P04 Baisse de la contribution au budget de l'Union | +0,00 | +0,00 | +0,00 | +0,36 | −3,41 |
| P05 Réorganisation de l'État (centralisation de la TVA, tra | −0,52 | −0,20 | −246,51 | +0,11 | +0,18 |
| P08 Âge légal ramené à 62 ans (60 ans pour les carrières co | −1,39 | −2,67 | −193,95 | +0,10 | −1,69 |
| P10 TVA ramenée de 20 % à 5,5 % sur l'électricité, le gaz,  | +0,09 | +0,02 | +26,49 | −0,29 | +2,98 |
| P11 Exonération d'impôt sur le revenu des moins de 30 ans ( | +0,02 | −0,02 | +7,86 | −0,05 | +0,50 |
| P12 Permis de conduire gratuit (18 ans, casier vierge) ; pr | +0,00 | −0,02 | +5,17 | −0,03 | +0,40 |
| P13 Part fiscale pleine dès le deuxième enfant | +0,04 | −0,00 | +13,62 | −0,08 | +0,74 |
| Σ mesures isolées | −2,02 | −3,07 | −444,57 | +0,39 | −2,46 |
| paquet complet (A) | −1,95 | −2,89 | −440,35 | +0,33 | −1,60 |
| interactions (A − Σ) | +0,07 | +0,18 | +4,22 | −0,06 | +0,85 |

**Tableau : effets des mesures isolées — Philippe (Horizons)** (régime principal ; chaque mesure simulée seule). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| mesure | PIB 5 ans (%) | PIB 10 ans (%) | emploi 5 ans (k) | solde 5 ans (pt) | dette 10 ans (pt) |
|---|---|---|---|---|---|
| H03 250 000 postes de fonctionnaires en moins (un départ su | −0,48 | −0,21 | −169,99 | +0,08 | +0,36 |
| H05 Âge de départ à 65 ans et 45 annuités ; départ précoce  | +0,21 | +0,83 | +32,18 | +0,06 | +0,37 |
| H06 Fin des 35 heures ; deux heures supplémentaires hebdoma | +1,59 | +1,96 | −336,35 | −0,28 | +3,70 |
| H08 Baisse de 30 % du nombre d'allocataires du RSA (accompa | +0,03 | +0,08 | −0,19 | +0,03 | +0,00 |
| H11 Baisse de 50 Md€ des impôts de production financée par  | −0,45 | −0,29 | −151,66 | −0,39 | +3,30 |
| H12 Fonds unique d'adaptation au changement climatique | +0,05 | +0,08 | +1,34 | −0,06 | +0,63 |
| Σ mesures isolées | +0,96 | +2,46 | −624,68 | −0,56 | +8,36 |
| paquet complet (A) | +0,96 | +2,45 | −622,43 | −0,57 | +8,42 |
| interactions (A − Σ) | +0,01 | −0,01 | +2,25 | −0,01 | +0,05 |

Les décompositions montrent que **les mesures qui modifient l'offre de travail sont les plus structurantes pour
l'activité à moyen terme**. Pour LFI et le RN, c'est la réforme des retraites (abaissement de l'âge et de la durée),
qui explique l'essentiel de l'effet négatif à dix ans sur le PIB. Pour Horizons, c'est d'abord la fin des 35 heures
(effet sur le PIB le plus important à cinq et dix ans, mais emploi en baisse, la production supplémentaire étant
obtenue par des heures plus longues), puis le relèvement de l'âge de départ, dont l'effet croît avec le temps. Pour
LFI, l'investissement hors budget est la mesure la plus favorable à l'activité à cinq ans, et les taxes sur le
patrimoine les premières par l'effet sur le solde ; pour le RN, la baisse de la contribution européenne et les
économies sur l'immigration portent l'essentiel de l'amélioration du solde. Pour Horizons, les suppressions de postes
publics et le pacte impôts de production / aides réduisent l'activité à court terme dans sa traduction centrale (la
moitié des aides supprimées étant des allègements de cotisations, la hausse du coût du travail l'emporte sur la baisse
des impôts de production). Les interactions entre mesures (paquet complet moins somme des effets isolés) sont faibles
pour le RN et Horizons ; elles sont plus importantes pour LFI, dont les mesures se renforcent mutuellement par les
prix et la fermeture.

## Lecture B : objectifs budgétaires {#sec:lecture-b}

La lecture B ajoute aux mesures documentées l'effort nécessaire pour suivre la trajectoire de solde annoncée. Elle
répond à la question : *si le programme atteignait l'objectif de déficit qu'il affiche, avec la composition de l'effort
qu'il revendique, quelles en seraient les conséquences macroéconomiques selon ce modèle ?*

**Tableau : lecture B (objectifs budgétaires).** Mesures documentées + effort supplémentaire pour suivre la trajectoire de solde annoncée, réparti selon les compositions du tableau du chapitre \ref{sec:prog-regimes}. Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — indicateur | 5 ans | 10 ans | 20 ans |
|---|---|---|---|
| Mélenchon (LFI) — PIB (%) | +2,7 | −1,2 | −2,7 |
| Mélenchon (LFI) — emploi (milliers) | +775,9 | −77,4 | −962,3 |
| Mélenchon (LFI) — chômage (pt) | −5,0 | −2,7 | −0,1 |
| Mélenchon (LFI) — pouvoir d'achat (%) | +5,6 | +3,5 | −2,0 |
| Mélenchon (LFI) — solde (pt PIB) | +2,8 | +4,1 | +7,9 |
| Mélenchon (LFI) — dette (pt PIB) | −18,7 | −36,1 | −83,3 |
| Mélenchon (LFI) — effort objectif (pt PIB) | −1,2 | +0,5 | +3,9 |
| Mélenchon (LFI) — niveau solde (% PIB) | −4,2 | −4,0 | −4,1 |
| Mélenchon (LFI) — niveau dette (% PIB) | +114,1 | +119,7 | +141,4 |
| Le Pen (RN) — PIB (%) | −9,6 | −11,1 | −6,6 |
| Le Pen (RN) — emploi (milliers) | −2560,6 | −4066,8 | −3091,8 |
| Le Pen (RN) — chômage (pt) | +4,7 | +8,5 | +5,3 |
| Le Pen (RN) — pouvoir d'achat (%) | −8,3 | −13,4 | −17,2 |
| Le Pen (RN) — solde (pt PIB) | +3,2 | +5,3 | +8,9 |
| Le Pen (RN) — dette (pt PIB) | +2,8 | −5,6 | −65,7 |
| Le Pen (RN) — effort objectif (pt PIB) | +7,8 | +13,3 | +15,1 |
| Le Pen (RN) — niveau solde (% PIB) | −3,8 | −2,9 | −3,1 |
| Le Pen (RN) — niveau dette (% PIB) | +135,6 | +150,1 | +159,0 |
| Philippe (Horizons) — PIB (%) | −5,2 | −3,5 | +1,1 |
| Philippe (Horizons) — emploi (milliers) | −2114,9 | −2450,6 | −1155,8 |
| Philippe (Horizons) — chômage (pt) | +6,9 | +8,8 | +6,0 |
| Philippe (Horizons) — pouvoir d'achat (%) | −11,1 | −16,7 | −21,6 |
| Philippe (Horizons) — solde (pt PIB) | +3,3 | +5,7 | +9,4 |
| Philippe (Horizons) — dette (pt PIB) | +3,4 | −11,6 | −77,1 |
| Philippe (Horizons) — effort objectif (pt PIB) | +8,0 | +12,1 | +13,7 |
| Philippe (Horizons) — niveau solde (% PIB) | −3,6 | −2,4 | −2,6 |
| Philippe (Horizons) — niveau dette (% PIB) | +136,2 | +144,2 | +147,5 |

**Tableau : atteinte des cibles de la lecture B** (solde simulé − cible annoncée).

| candidat | cible annoncée | écart moyen à la cible 2028-2032 (pt) | écart maximal (pt) |
|---|---|---|---|
| Mélenchon (LFI) | réduction du déficit de 24,7 Md€ en 2027 (mesures) puis stabilisation du ratio dette/PIB en un quinquennat | −0,00 | +0,06 |
| Le Pen (RN) | déficit à 3 % du PIB en 2030 ; dette de 121 % (2027) à 112 % (2032) ; 140 Md€ d'économies | −0,52 | −0,91 |
| Philippe (Horizons) | déficit sous 2,5 % du PIB en fin de quinquennat ; moitié de l'effort sur les dépenses sociales, un quart sur l'État et les collectivités, un quart « sur la croissance » ; aucun nouvel impôt | −0,34 | −0,45 |

**Tableau : niveaux de solde et de dette publics (% du PIB), lectures A et B, sous deux hypothèses de taux longs** (OAT à 4,89 %, dernier point observé, ou à 3,82 %, moyenne des douze derniers mois). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — lecture | solde 5 ans (% PIB) | solde 10 ans (% PIB) | dette 5 ans (% PIB) | dette 10 ans (% PIB) | dette 20 ans (% PIB) | effort B 10 ans (pt) |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) — A | −3,7 | −4,4 | 112,7 | 117,7 | 151,0 | 0,0 |
| Mélenchon (LFI) — B | −4,2 | −4,0 | 114,1 | 119,7 | 141,4 | 0,5 |
| Mélenchon (LFI) — A, OAT 3,82 % | −2,8 | −3,3 | 111,1 | 111,3 | 127,6 | 0,0 |
| Mélenchon (LFI) — B, OAT 3,82 % | −4,1 | −4,0 | 113,2 | 116,7 | 135,9 | −2,0 |
| Le Pen (RN) — A | −6,7 | −8,1 | 132,5 | 154,2 | 221,3 | 0,0 |
| Le Pen (RN) — B | −3,8 | −2,9 | 135,6 | 150,1 | 159,0 | 13,3 |
| Le Pen (RN) — A, OAT 3,82 % | −5,7 | −6,6 | 130,7 | 146,3 | 191,2 | 0,0 |
| Le Pen (RN) — B, OAT 3,82 % | −3,1 | −2,9 | 133,5 | 141,8 | 146,1 | 9,8 |
| Philippe (Horizons) — A | −7,5 | −8,7 | 138,1 | 164,2 | 237,8 | 0,0 |
| Philippe (Horizons) — B | −3,6 | −2,4 | 136,2 | 144,2 | 147,5 | 12,1 |
| Philippe (Horizons) — A, OAT 3,82 % | −6,6 | −7,1 | 136,2 | 156,0 | 206,2 | 0,0 |
| Philippe (Horizons) — B, OAT 3,82 % | −3,1 | −2,4 | 134,3 | 138,8 | 139,5 | 9,4 |

**Lecture.** L'effort supplémentaire nécessaire est très différent selon les candidats, parce que leurs mesures
documentées ne partent pas du même point et que leurs cibles diffèrent :

- pour **LFI**, dont les mesures documentées améliorent déjà fortement le solde, la cible de stabilisation de la dette
  en 2032 est atteinte sans effort supplémentaire à court terme (l'effort B est même négatif jusqu'à la fin du
  quinquennat, ce qui revient à autoriser des dépenses ou des baisses d'impôts supplémentaires) ; il devient positif
  ensuite, pour compenser la dérive de la référence ;
- pour le **RN** et **Horizons**, l'effort non ventilé est considérable : plusieurs points de PIB dès cinq ans, plus de
  dix points à dix ans dans l'hypothèse de taux de 4,89 %. Il s'agit d'une consolidation budgétaire d'ampleur
  historique, dont le modèle prévoit des effets récessifs importants (PIB inférieur de plusieurs points à la
  référence, chômage nettement plus élevé, pouvoir d'achat en baisse) ;
- l'**hypothèse de taux** modifie fortement l'effort : avec une OAT à 3,82 %, la dérive de la référence est moindre et
  l'effort nécessaire plus faible.

Ces résultats ne sont pas des prévisions : ils mesurent l'écart entre les objectifs annoncés et la dynamique spontanée
de la dette dans ce modèle. Ils dépendent de la référence (convention de dépense, taux), des multiplicateurs (élevés
dans le régime principal) et de la composition supposée de l'effort. Un gouvernement qui annoncerait un tel effort
bénéficierait peut-être d'une baisse de la prime de risque (non représentée dans le régime principal) ; il pourrait
aussi ne pas le réaliser. La comparaison A/B rend visible le fait que **les mesures documentées du RN et d'Horizons
ne représentent qu'une faible part de l'effort nécessaire à leurs objectifs**, alors que les mesures de LFI dépassent,
à court terme, l'effort requis par son objectif — sous les hypothèses favorables de traduction de ses recettes.

## Effets des régimes budgétaires et monétaires {#sec:effets-regimes}

**Tableau : lecture A sous les dix régimes de robustesse** (fourchette des effets, régimes extrêmes, stabilité du signe). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — indicateur — horizon | principal | minimum | maximum | régime du minimum | régime du maximum | signe robuste |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) — PIB (%) — 5 ans | +1,84 | +0,96 | +2,84 | R2, fermeture rapide | R2, fermeture lente | oui |
| Mélenchon (LFI) — PIB (%) — 10 ans | −0,54 | −1,47 | +0,91 | R2, fermeture rapide | R2, fermeture lente | non |
| Mélenchon (LFI) — PIB (%) — 20 ans | −1,07 | −2,13 | +0,40 | R2 active symétrique | R2, fermeture lente | non |
| Mélenchon (LFI) — chômage (pt) — 5 ans | −4,51 | −4,96 | −4,08 | R2, fermeture lente | R2, fermeture rapide | oui |
| Mélenchon (LFI) — chômage (pt) — 10 ans | −2,78 | −3,79 | −2,09 | R2, fermeture lente | R2, fermeture rapide | oui |
| Mélenchon (LFI) — chômage (pt) — 20 ans | −1,39 | −2,37 | −0,28 | R2, fermeture lente | R2 active symétrique | oui |
| Mélenchon (LFI) — dette (pt PIB) — 5 ans | −20,11 | −26,85 | −16,63 | R2, ancrage faible | R2, ancrage fort | oui |
| Mélenchon (LFI) — dette (pt PIB) — 10 ans | −38,14 | −56,96 | −27,86 | R2, ancrage faible | R2, ancrage fort | oui |
| Mélenchon (LFI) — dette (pt PIB) — 20 ans | −73,61 | −118,84 | −48,09 | R2, ancrage faible | R2, ancrage fort | oui |
| Le Pen (RN) — PIB (%) — 5 ans | −1,95 | −2,03 | −1,27 | R2 active symétrique | R2, fermeture sur le chômage | oui |
| Le Pen (RN) — PIB (%) — 10 ans | −2,89 | −3,38 | −2,66 | R2 active symétrique | R2, fermeture lente | oui |
| Le Pen (RN) — PIB (%) — 20 ans | −3,64 | −4,50 | −3,21 | R2 active symétrique | R2, fermeture lente | oui |
| Le Pen (RN) — chômage (pt) — 5 ans | −1,84 | −2,20 | −1,82 | R2, fermeture sur le chômage | R2, fermeture rapide | oui |
| Le Pen (RN) — chômage (pt) — 10 ans | −1,65 | −1,78 | −1,30 | R2, fermeture lente | R2 active symétrique | oui |
| Le Pen (RN) — chômage (pt) — 20 ans | −1,08 | −1,39 | −0,15 | R2, fermeture lente | R2 active symétrique | oui |
| Le Pen (RN) — dette (pt PIB) — 5 ans | −0,34 | −1,91 | +0,10 | R2, fermeture sur le chômage | R2, ancrage fort | non |
| Le Pen (RN) — dette (pt PIB) — 10 ans | −1,60 | −6,21 | +0,74 | R2, ancrage faible | R2, ancrage fort | non |
| Le Pen (RN) — dette (pt PIB) — 20 ans | −3,34 | −18,03 | +4,56 | R2, ancrage faible | R2, ancrage fort | non |
| Philippe (Horizons) — PIB (%) — 5 ans | +0,96 | +0,19 | +2,09 | R2, fermeture sur le chômage | R2 active symétrique | oui |
| Philippe (Horizons) — PIB (%) — 10 ans | +2,45 | +1,67 | +4,47 | R2, fermeture lente | R2 active symétrique | oui |
| Philippe (Horizons) — PIB (%) — 20 ans | +4,08 | +2,97 | +5,55 | R2, fermeture lente | R2 active symétrique | oui |
| Philippe (Horizons) — chômage (pt) — 5 ans | +2,56 | +1,70 | +3,04 | R2 active symétrique | R2, fermeture sur le chômage | oui |
| Philippe (Horizons) — chômage (pt) — 10 ans | +2,56 | +0,69 | +3,05 | R2 active symétrique | R2, fermeture lente | oui |
| Philippe (Horizons) — chômage (pt) — 20 ans | +1,93 | +0,07 | +2,70 | R2 active symétrique | R2, fermeture lente | oui |
| Philippe (Horizons) — dette (pt PIB) — 5 ans | +5,28 | +3,91 | +8,01 | R2, ancrage fort | R2, ancrage faible | oui |
| Philippe (Horizons) — dette (pt PIB) — 10 ans | +8,42 | +3,93 | +17,50 | R2, ancrage fort | R2, ancrage faible | oui |
| Philippe (Horizons) — dette (pt PIB) — 20 ans | +13,21 | −1,48 | +42,78 | R2, ancrage fort | R2, ancrage faible | non |

Les régimes modifient surtout l'ampleur des effets sur la dette (règle active, réaction de la BCE et prime
souveraine) et sur le chômage (vitesse de fermeture), beaucoup moins le signe des effets sur le PIB. Le régime « sans
règle budgétaire » (R0) et les régimes « ancrage faible » ou « BCE + prime » amplifient les effets sur la dette ;
« fermeture sur le chômage » et « R2 active symétrique » modifient la dynamique du chômage.

## Effets des réactions européennes et de la mise en œuvre {#sec:effets-ue-moe}

**Tableau : variantes européennes (régime BCE + prime pour les trois) et mise en œuvre partielle (50 %) ou retardée (2 ans) ; pour LFI, additionnalité de l'investissement hors budget (100 % dans la lecture A ; régime principal)** (écarts à la référence du régime correspondant). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — variante | PIB 5 ans (%) | PIB 10 ans (%) | chômage 5 ans (pt) | solde 5 ans (pt) | dette 10 ans (pt) | dette 20 ans (pt) |
|---|---|---|---|---|---|---|
| Mélenchon (LFI) — conforme | +1,79 | −0,61 | −4,49 | +3,18 | −36,90 | −74,54 |
| Mélenchon (LFI) — contentieux | +2,03 | −0,45 | −4,36 | +3,00 | −35,07 | −72,28 |
| Mélenchon (LFI) — tension | +2,04 | −0,45 | −4,36 | +2,88 | −34,45 | −73,52 |
| Mélenchon (LFI) — partielle 50 | +0,96 | −0,29 | −2,27 | +1,52 | −16,86 | −31,91 |
| Mélenchon (LFI) — retard 2ans | +3,00 | +0,10 | −4,33 | +2,72 | −31,77 | −67,22 |
| Mélenchon (LFI) — investissement hors APU additionnel à 50 % | +0,93 | −0,89 | −3,82 | +2,61 | −30,13 | −55,98 |
| Mélenchon (LFI) — investissement hors APU additionnel à 25 % | +0,47 | −1,06 | −3,47 | +2,24 | −26,02 | −47,25 |
| Mélenchon (LFI) — investissement hors APU additionnel à 0 % | +0,02 | −1,24 | −3,12 | +1,87 | −21,85 | −38,50 |
| Le Pen (RN) — conforme | −1,93 | −2,84 | −1,84 | +0,40 | −2,79 | −11,57 |
| Le Pen (RN) — contentieux | −1,99 | −2,86 | −1,79 | +0,17 | −0,94 | −6,83 |
| Le Pen (RN) — tension | −1,99 | −2,86 | −1,79 | −0,05 | +0,84 | −3,76 |
| Le Pen (RN) — partielle 50 | −0,89 | −1,32 | −0,82 | +0,17 | −0,58 | −1,10 |
| Le Pen (RN) — retard 2ans | −1,41 | −2,66 | −1,73 | +0,39 | −1,10 | −3,00 |
| Philippe (Horizons) — conforme | +0,97 | +2,43 | +2,56 | −0,56 | +8,75 | +20,56 |
| Philippe (Horizons) — contentieux | +0,97 | +2,43 | +2,56 | −0,56 | +8,75 | +20,56 |
| Philippe (Horizons) — tension | +0,97 | +2,43 | +2,56 | −0,84 | +11,17 | +26,38 |
| Philippe (Horizons) — partielle 50 | +0,63 | +1,58 | +1,56 | −0,24 | +4,36 | +6,67 |
| Philippe (Horizons) — retard 2ans | +0,38 | +2,01 | +2,53 | −0,73 | +8,05 | +13,96 |

**Réactions européennes.** Pour LFI, les variantes « contentieux » et « tension » retardent d'un an
l'investissement hors budget et la taxe sur les multinationales (mesures de niveau 1), ce qui déplace l'effet
d'activité sans en changer l'ordre de grandeur. Pour le RN, la variante « contentieux » supprime l'économie sur la
contribution européenne et réduit de moitié la baisse de TVA sur l'énergie : le solde est un peu moins favorable et la
dette plus élevée. Les amendes de la procédure de déficit excessif (0,1 point de PIB pendant deux ans) et le choc de
prime de 50 points de base de la variante « tension » ont des effets modestes sur la dette à cinq ans. Pour Horizons,
dont les mesures documentées ne posent pas de problème de compatibilité, « conforme » et « contentieux » sont identiques ;
seules les amendes et le choc de prime distinguent la variante « tension ».

**Additionnalité de l'investissement hors budget (LFI).** La lecture A suppose que les 100 Md€ annuels
d'investissement portés par le pôle public bancaire s'ajoutent entièrement à l'investissement qui aurait eu lieu
sans eux (borne haute). Les variantes à 50 %, 25 % et 0 % montrent que **cette hypothèse détermine à elle seule le
signe de l'effet d'activité de court terme du paquet LFI** : l'écart de PIB à cinq ans, positif dans la lecture A,
devient proche de zéro sans additionnalité, tandis que l'amélioration du solde et la baisse du ratio de dette sont
réduites (le PIB nominal plus élevé et les recettes induites expliquaient une partie de la baisse du ratio). Le
tableau précédent donne les valeurs ; ni le financement de ces investissements (épargne réglementée, crédit) ni leur
éventuelle requalification en dette publique ne sont représentés.

**Mise en œuvre partielle ou retardée.** Une mise en œuvre à 50 % divise approximativement les effets par deux (les
effets sont presque linéaires à cette échelle) ; un retard de deux ans décale les effets de court terme sans changer
les effets à vingt ans de manière importante.

## Environnements alternatifs {#sec:effets-environnements}

**Tableau : lecture A dans les environnements alternatifs** (σ = 0,3 et 0,6 ; équation de prix v0.9). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — environnement | PIB 10 ans (%) | emploi 10 ans (k) | chômage 10 ans (pt) | dette 10 ans (pt) | dette 20 ans (pt) |
|---|---|---|---|---|---|
| Mélenchon (LFI) — P4 (référence) | −0,54 | −48,77 | −2,78 | −38,14 | −73,61 |
| Mélenchon (LFI) — p4_sigma03 | −0,61 | −7,09 | −2,91 | −39,63 | −77,72 |
| Mélenchon (LFI) — p4_sigma06 | −0,50 | −72,54 | −2,71 | −36,59 | −69,83 |
| Mélenchon (LFI) — p4_prix_v09 | −0,59 | −53,59 | −2,77 | −38,32 | −75,94 |
| Le Pen (RN) — P4 (référence) | −2,89 | −754,30 | −1,65 | −1,60 | −3,34 |
| Le Pen (RN) — p4_sigma03 | −2,90 | −774,49 | −1,58 | −1,19 | −2,28 |
| Le Pen (RN) — p4_sigma06 | −2,90 | −708,66 | −1,79 | −2,51 | −5,75 |
| Le Pen (RN) — p4_prix_v09 | −2,88 | −760,36 | −1,63 | −1,15 | −2,15 |
| Philippe (Horizons) — P4 (référence) | +2,45 | −267,47 | +2,56 | +8,42 | +13,21 |
| Philippe (Horizons) — p4_sigma03 | +2,43 | −132,25 | +2,17 | +6,38 | +6,57 |
| Philippe (Horizons) — p4_sigma06 | +2,47 | −414,68 | +2,98 | +10,30 | +21,21 |
| Philippe (Horizons) — p4_prix_v09 | +2,43 | −256,45 | +2,52 | +7,82 | +11,97 |

L'élasticité de substitution capital-travail ($\sigma$) et l'équation des prix de la valeur ajoutée modifient
l'ampleur des effets sur l'emploi et la dette, sans changer leur sens.

## Trajectoires {#sec:trajectoires}

```{=latex}
\begin{figure}[htbp]\centering\includegraphics[width=0.95\textwidth]{figures/f9_pib.pdf}\caption{PIB : écart à la référence (lectures A et B).}\end{figure}
```
```{=latex}
\begin{figure}[htbp]\centering\includegraphics[width=0.95\textwidth]{figures/f9_chomage.pdf}\caption{Chômage : écart à la référence (points).}\end{figure}
```
```{=latex}
\begin{figure}[htbp]\centering\includegraphics[width=0.95\textwidth]{figures/f9_solde.pdf}\caption{Solde public en niveau (lectures A et B ; référence en gris).}\end{figure}
```
```{=latex}
\begin{figure}[htbp]\centering\includegraphics[width=0.95\textwidth]{figures/f9_dette.pdf}\caption{Dette publique en niveau, OAT à 4,89 \% (référence en gris).}\end{figure}
```
```{=latex}
\begin{figure}[htbp]\centering\includegraphics[width=0.95\textwidth]{figures/f9_dette_oat.pdf}\caption{Dette publique en niveau, OAT à 3,82 \%.}\end{figure}
```


## Indicateurs détaillés {#sec:indicateurs-detail}

Les tableaux complets (dix-sept indicateurs, trois horizons, deux lectures) figurent en annexe \ref{sec:annexe-e}. Les
indicateurs couverts sont : PIB, emploi, chômage, salaire réel, prix à la consommation, pouvoir d'achat (revenu
disponible réel), consommation, taux d'épargne, investissement, taux de marge, exportations, importations, solde
public, dette publique, charge d'intérêts, recettes et dépenses publiques (en points de PIB).

## Ce qui n'a pas été simulé {#sec:non-simule}

- Les mesures non chiffrées ou sans canal (liste au chapitre \ref{sec:programmes}) : impôt sur le revenu à 14 tranches,
  allocation familiale de 350 €, durée d'indemnisation du chômage, jours de carence, pilier de capitalisation, contrôle
  des capitaux, priorité nationale, planification industrielle, nucléaire.
- La variante de mandat de LFI (retraite à 60 ans et 40 annuités) n'est pas incluse dans le paquet de base.
- Les effets distributifs dynamiques (M16) et les effets territoriaux.
- Le financement de l'investissement hors budget (centralisation de l'épargne réglementée, crédit du pôle public) et
  le risque de requalification de sa dette en dette publique.
