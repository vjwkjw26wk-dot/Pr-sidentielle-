# Chantier C — validation prédictive (phase 4.3)

Module `src/m22_validation.py` ; scripts `c1_ex_ante.py` (rétrosimulations conditionnelles et prévisions ex ante,
mêmes origines), `c1_synthese.py`, `c2_choc_cice.py` (choc de politique identifié). Résultats : `resultats/c1_*.json`,
`resultats/c1_erreurs.csv`, `resultats/c2_choc_cice.json`.

## 1. Protocole : quatre niveaux distincts

| Niveau | Coefficients | Exogènes et politiques | Ce que l'on mesure |
|---|---|---|---|
| 1. Dans l'échantillon | estimés sur la période | observés | ajustement des équations (rapports M7, M18, M19, M21) |
| 2. Conditionnel hors échantillon | estimés jusqu'à l'origine | observés ex post | erreur du modèle lui-même |
| 3. Ex ante | estimés jusqu'à l'origine | connus à l'origine (millésime d'octobre du FMI ; conventions) | erreur d'une prévision faite avec le modèle, comparée au FMI et à une prévision naïve |
| 4. Choc de politique | estimés jusqu'à l'origine | observés, avec ou sans la politique | effet d'une politique identifiée, comparé aux évaluations ex post |

Conventions ex ante (aucune information postérieure à l'origine B) :
- demande extérieure : importations en volume de la zone euro prévues par le FMI en octobre B ;
- taux d'intérêt constants ;
- législation de B maintenue (taux d'IS, prélèvements, CICE au taux de B, pas de bascule de 2019) ;
- autres exogènes prolongées à leur croissance moyenne des cinq années précédentes ;
- potentiel et chômage structurel en temps réel.

Classement des variables (`m22_validation.CLASSEMENT`) :
- **imposées** : environnement international, taux, volumes publics, population active, politiques fiscales sous forme de
  taux apparents, CICE, taux apparent de l'IS ;
- **partiellement imposées** : recettes et dépenses publiques, IS, intérêts des sociétés ;
- **prédites** : demande, production, emploi, chômage, prix, salaires, marges, comptes des sociétés et des ménages,
  solde et dette.

Origines : 2010, 2012, 2014, 2016 (horizons de 1, 3 et 5 ans, dans la limite de 2019) et 2021 (1 et 3 ans).
Configurations : v0.9, T1, P4 (T1 + compte des sociétés).

## 2. Résultats (erreur absolue moyenne, origines 2010-2016)

| Variable, horizon | P4 conditionnel | P4 ex ante | FMI (même millésime) | Naïf |
|---|---|---|---|---|
| Croissance du PIB, 1 an (pt) | 0,88 | **0,39** | 0,59 | 0,84 |
| Croissance du PIB, 5 ans (pt/an) | 0,09 | **0,25** | 0,34 | 0,38 |
| Inflation, 1 an (pt) | 0,44 | 0,72 | **0,43** | 0,53 |
| Inflation, 5 ans (pt/an) | 0,39 | 0,59 | **0,46** | 0,47 |
| Chômage, 1 an (pt) | 0,38 | **0,22** | 0,32 | 0,35 |
| Chômage, 5 ans (pt) | 0,32 | 1,37 | **1,17** | 1,04 |
| Solde public, 3 ans (pt de PIB) | 0,59 | 1,45 | **0,91** | 1,52 |
| Dette publique, 5 ans (pt de PIB) | 4,51 | 10,59 | **6,93** | 12,25 |

Lecture :
1. **Croissance.** En prévision ex ante, le modèle fait mieux que le FMI du même millésime et que la prévision naïve. Ce
   n'est pas un critère d'ajustement : les coefficients sont estimés jusqu'à l'origine.
2. **Inflation.** Biais négatif de 0,3 à 0,4 point par an en conditionnel, déjà diagnostiqué au chantier A (équation de
   salaires).
3. **Solde et dette ex ante.** Biais vers le haut de la dette (+10,6 points à 5 ans) dû à la convention de législation
   inchangée : la consolidation de 2011-2014 n'est pas connue à l'origine. Le FMI intègre les mesures annoncées. En
   conditionnel, l'erreur de dette tombe à 4,5 points : l'essentiel de l'écart ex ante vient des politiques, pas du modèle.
4. **Chômage à 5 ans.** Correct en conditionnel (0,3), mais les erreurs ex ante d'exogènes (population active, volumes
   publics) dominent.
5. **v0.9, T1 et P4.** Écarts entre configurations faibles à ces horizons : moins de 0,05 point sur la croissance,
   0,15 point au plus sur l'inflation (v0.9 meilleure en conditionnel, moins bonne ex ante), 0,6 point au plus sur la dette.
   Les gains de T1 et P4 portent sur l'ancrage et les mécanismes, pas sur l'ajustement.

**Origine 2021 (choc énergétique).** Toutes les méthodes sous-estiment l'inflation : FMI −4,3 points la première année,
P4 ex ante −3,6, P4 conditionnel −1,0. En conditionnel, la croissance est sous-estimée de 1,3 à 1,7 point par an et la
dette surestimée de 16 points à 3 ans. 2022-2024 sort du cadre estimé : salaires, profits exceptionnels, mesures de
protection des ménages. Les mesures sont dans les dépenses observées injectées, mais leurs effets sur les prix ne sont pas
modélisés.

## 3. Choc de politique : CICE (niveau 4)

Rétrosimulation conditionnelle 2012-2018, avec CICE observé − sans CICE ; coût budgétaire compté dans la différence.

| Emploi marchand (milliers) | 2014 | 2016 | 2017 |
|---|---|---|---|
| v0.9 | +37 | +64 | +76 |
| T1 | +36 | +68 | +83 |
| P4 | +38 | +71 | +86 |

Évaluations ex post (France Stratégie, 2020) : environ 100 000 emplois en micro-économétrie (2013-2016) et environ
160 000 en évaluation macro-sectorielle (2013-2017) ; la Banque de France trouve davantage pour CICE et Pacte cumulés,
sur une période plus longue.

En P4, le CICE fait aussi baisser les prix à la consommation de 1,4 % en 2016, augmenter le taux de marge de
0,4 point et dégrade le solde public de 0,6 point de PIB.

Le modèle est en dessous des évaluations, mais P4 s'en rapproche plus que la v0.9. Deux raisons :
- la transmission aux prix est plus forte que celle mesurée ex post ;
- la substitution capital-travail est modérée (σ = 0,45).

## 4. Interactions et incohérences relevées et traitées pendant le chantier C

| Constat | Traitement |
|---|---|
| L'IS proportionnel au taux légal contredit les données (élasticité du taux apparent −0,10 ± 0,29) | compte des sociétés : taux apparent observé injecté en rétrosimulation ; taux légal réservé aux mesures |
| Le millésime 2010-10 du FMI ne couvre que B et B+1 dans DBnomics | dernière croissance prévue prolongée (documenté) |
| L'exogène observée de demande (importations de l'UE) n'a pas d'équivalent dans les agrégats du FMI | proxy zone euro (agrégat 163) |
| Le coût budgétaire du CICE est dans les dépenses observées des deux rétrosimulations | ajouté en dépense dans le test de politique (différence avec − sans) |
