# Boucle de cohérence des effets de mesures et jeux de mesures des candidats (17 novembre 2026)

## 1. Boucle de cohérence

Méthode : pour chacune des variantes élémentaires précalculées (une mesure à la fois, entrée en vigueur en 2028),
l'effet statique sur les finances publiques et l'effet macroéconomique ont été comparés à des chiffrages publics
indépendants. Un écart de plus de 30 % sans explication par une différence de périmètre est traité comme une anomalie.

| Mesure | Modèle | Repère public | Verdict |
|---|---|---|---|
| CSG sur les revenus d'activité +1 pt | 11,4 Md€ | environ 17 Md€ pour +1 pt sur toutes les assiettes (activité, remplacement, capital) | cohérent (périmètre activité seule) |
| TVA taux normal +1 pt / taux réduits +1 pt | 8,2 + 5,0 = 13,2 Md€ | IPP : environ 13 Md€ pour +1 pt sur tous les taux | cohérent |
| Impôt sur la fortune, taux moyen 0,5 % | 4,7 Md€ avant comportements | ordre de grandeur des rendements de l'ISF avant 2018 (4 à 5 Md€) | cohérent |
| Impôt sur le revenu, 1re tranche +1 pt | 4,5 Md€ | 3 à 4,5 Md€ selon les sources | haut de fourchette, accepté |
| Prime d'activité +10 % | 0 Md€ (avant correction) | environ 1 Md€ | **anomalie corrigée** : la réforme OpenFisca démarrait le 1er octobre 2024 et n'était pas vue par les années simulées ; date d'effet ramenée au 1er janvier 2024 (+2,6 Md€ versés pour +10 % avec les effets de bord du barème) |
| Abrogation de la réforme de 2023 (retour à 62 ans) | 1,7 à 2 fois le chiffrage officiel | 14,1 Md€ en 2030, 8,2 Md€ en 2027 (estimations publiques de l'abrogation) | **anomalie corrigée** : la pension supplémentaire des départs avancés était comptée à la pension moyenne ; coefficient de pension marginale de 0,55 (carrières plus courtes, décote, pensions plus faibles des départs anticipés) calé sur le chiffrage officiel |
| SMIC +1 % hors inflation | aucun coût public | 0,5 à 0,8 Md€ par point (allègements généraux, prime d'activité, rémunérations publiques) | **anomalie corrigée** : coût public de 660 M€ par point ajouté |
| Impôts de production −15 Md€ | solde −0,53 pt de PIB en 2028, PIB +0,06 % | — | nouvelle mesure (CVAE, CFE, C3S), effet sur les prix de valeur ajoutée (répercussion 50 %) |
| Recettes sans effet sur la demande +10 Md€ | solde +0,33 pt de PIB | 10 Md€ ≈ 0,33 pt de PIB | cohérent par construction (ligne de transparence) |

Les autres variantes (emploi public, dépenses par fonction, cotisations, IS, âge légal, indexation, droits de douane,
taxe carbone, temps de travail) ont des multiplicateurs et des rendements dans les fourchettes déjà documentées
dans 07_validation_integrale.md et M7_M8_comportements_et_bouclage.md.

## 2. Jeux de mesures des candidats

Fichier : `simulateur/programmes.py`. Dans l'interface, le sélecteur « Charger les propositions d'un candidat »
positionne les curseurs ; ils restent modifiables. Pour chaque jeu, l'interface affiche les sources, la correspondance
mesure → curseur, les mesures non représentées et le total annoncé par le candidat.

Règles communes (identiques pour tous) :
- seules les mesures identifiables et chiffrées dans des sources publiques sont traduites ;
- les totaux d'économies annoncés ne sont pas complétés par des économies non détaillées ;
- montant cumulé sur cinq ans → montant annuel de fin de mandat = cumul ÷ 3 ; montant pluriannuel sans durée → réparti sur cinq ans ;
- taux non précisé → convention signalée ;
- candidats sans chiffrage fiable à la date des sources : non traduits, listés comme tels.

Jeux disponibles (ordre alphabétique) : Gabriel Attal (Renaissance), Raphaël Glucksmann (Place publique – PS),
Marine Le Pen (RN), Jean-Luc Mélenchon (LFI), Édouard Philippe (Horizons), Bruno Retailleau (LR).
Non traduits : Marine Tondelier, Fabien Roussel, Éric Zemmour et les autres candidats déclarés.

Nouveaux curseurs créés pour ces traductions, utilisables par tous : « Impôts de production » et « Recettes ou
économies sans effet sur la demande ». Plages étendues : emplois publics jusqu'à −500 000 ; pas plus fins pour la TVA,
les transferts aux ménages et l'indexation des pensions.

Limites principales :
- les programmes sont incomplets à cette date et évoluent ; les jeux devront être mis à jour ;
- les mesures non chiffrées (décote, capitalisation, blocage des prix, 32 heures sans paramètres, préférence nationale…)
  ne sont pas simulées, ce qui biaise chaque jeu dans un sens propre à chacun ;
- les conventions de taux (ISF, tranche supérieure, successions) sont des hypothèses du modélisateur.

Résultats simulés par le modèle complet : outputs/programmes_candidats.md (script tests/programmes_candidats.py).

### Résultats 2032 (modèle complet version 0.6, écart à la trajectoire inchangée ; plages de sensibilité : 13_contre_expertise.md)

| Candidat | PIB (%) | Chômage (pt) | Emploi (milliers) | Prix (%) | Solde (pt PIB) | Dette (pt PIB) |
|---|---|---|---|---|---|---|
| Gabriel Attal | -0.28 | +0.24 | -83 | -0.16 | +0.26 | -0.26 |
| Raphaël Glucksmann | -0.22 | -1.81 | -157 | +1.58 | -1.57 | +3.99 |
| Marine Le Pen | -1.62 | -1.06 | -439 | -0.02 | -0.24 | +1.52 |
| Jean-Luc Mélenchon | -0.98 | -2.85 | -177 | +3.35 | -1.17 | +0.21 |
| Édouard Philippe | -0.17 | +0.52 | -72 | -0.69 | +0.41 | +0.32 |
| Bruno Retailleau | -0.93 | +0.95 | -321 | -1.43 | +0.33 | +2.40 |

Lecture des contrôles de cohérence sur ces jeux :
- Les baisses du chômage associées à des baisses de l'emploi (retour à 62 ou 60 ans) viennent de la réduction de la population active : à court terme, le modèle fait porter l'ajustement sur le chômage, puis la boucle prix-salaires réduit l'emploi. Résultat dépendant des hypothèses (courbe de salaires, absence de substitution entre générations).
- Les variations d'emplois publics atteignent désormais leur cible en cinq ans (auparavant immédiates), ce qui supprimait un choc irréaliste en 2028 pour les jeux comportant des non-remplacements.
- Écart de l'approximation additive de l'interface en 2032 : au plus 0,15 point de dette et 0,08 point de prix sur les six jeux.
