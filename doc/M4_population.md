# Module M4 — Population de ménages et de foyers fiscaux (version 1.3)

**Statut : construit pour l'impôt sur le revenu, sous réserve (16 novembre 2026, soir).**
- Validé : structure des ménages ; impôt au barème par décile de revenu fiscal par part (écart total +2 %).
- Restent calés, et non testés : le capital au prélèvement forfaitaire et les réductions et crédits non modélisés un à un.
- Prestations : première version. RSA, allocations familiales et aides au logement sont cohérents ; les éligibles à la prime d'activité sont sous-estimés.
- Non construits : les 3 millions de foyers hors champ.

## Base : de vrais ménages
Le fichier détail du recensement 2022 (Insee, « Individus localisés à la région », licence ouverte, 17,5 millions d'individus pondérés) fournit des ménages réels anonymisés. Il donne pour chaque personne :
- les liens familiaux (identifiant de ménage, lien à la personne de référence, famille) ;
- l'âge, le sexe et le statut conjugal ;
- l'activité, le statut salarié ou non, le groupe socioprofessionnel et le temps partiel ;
- les études et le lieu de travail.

Aucune structure familiale n'est inventée (révision de la décision A4).

Échantillon de travail : tirage aléatoire de 2 % des ménages ordinaires (163 826 ménages, 344 527 personnes, 201 821 foyers), poids = poids Insee / 0,02.

## Construction
1. **Foyers fiscaux.**
   - Les adultes mariés ou pacsés d'une même famille déclarent ensemble ; les concubins séparément.
   - Les enfants de moins de 18 ans, ou de moins de 25 ans s'ils étudient, sont rattachés au premier adulte de la famille.
   - Un parent isolé avec des personnes à charge reçoit la case T.
2. **Rang de revenu.** Chaque adulte reçoit un score latent tiré de grilles publiées : salaires en équivalent temps plein 2024 par catégorie socioprofessionnelle et sexe (Insee), pensions de droit direct par sexe (DREES), forfaits pour les autres situations. Le score ne sert qu'à classer les foyers.
3. **Niveau de revenu.** Chaque foyer reçoit le revenu fiscal de référence de son rang dans la distribution DGFiP (IRCOM 2025, revenus 2024, 25 tranches). Salaires et pensions déclarés suivent les rapports publiés par tranche.
4. **Corrections tirées des statistiques nationales par case de déclaration** (DGFiP, `ir-declarations-2042-nat`, revenus 2024) :
   - heures supplémentaires exonérées (21,8 Md€, cases 1GH à 1JH) retirées des salaires imposables ;
   - salaires des personnes travaillant à l'étranger (lieu de travail du recensement) déclarés comme revenus à crédit égal à l'impôt français (case 8TK) : 15,0 Md€, contre 19,7 Md€ déclarés, non-résidents compris ;
   - épargne retraite déductible (9,6 Md€, cases 6NS, 6RS, 6QS…), réintégrée dans le revenu fiscal.
5. **Reste** = revenu fiscal visé − revenu fiscal OpenFisca des salaires et pensions − heures supplémentaires (239 Md€). Il est réparti par ajustement biproportionnel (RAS) par tranche entre trois postes :
   - le capital au prélèvement forfaitaire unique (dividendes, intérêts, plus-values : 79 Md€ déclarés) ;
   - les revenus fonciers et d'indépendants au barème (103 Md€) ;
   - l'excédent (17 % du reste), traité comme inclus dans le revenu fiscal mais non imposé au barème (revenus étrangers, plus-values en report, revenus exonérés, abattements réintégrés).

   Le capital et l'excédent sont concentrés vers le haut (η = 0,8), le barème l'est peu (0,2) ; les foyers d'indépendants reçoivent davantage de revenus au barème.

   **Version 1.3** : deux contraintes supplémentaires.
   - Le capital au prélèvement forfaitaire est calé dans chaque décile de revenu fiscal par part sur le montant publié par la DGFiP (prélèvement par part / 12,8 %).
   - Les revenus au barème sont recalés sur leur masse nationale déclarée (103 Md€). Le reste non affecté (57 Md€) est inclus dans le revenu fiscal mais non imposé au barème.
6. **Dépenses ouvrant droit à crédits ou réductions** (emploi à domicile, garde d'enfants, dons) : nombres de foyers et montants nationaux reproduits. Les autres réductions et crédits (investissements locatifs, souscriptions, outre-mer…) sont calés par décile de revenu fiscal par part sur le tableau DGFiP. Ils sont alors des données d'entrée, et non un test.
7. **Impôt** : OpenFisca-France 177 (barème, quotient familial, décote, prélèvement forfaitaire unique, crédits et réductions modélisés). La contribution sur les hauts revenus est calculée directement sur le revenu fiscal, car sa variable OpenFisca dépasse la mémoire disponible. Le seuil de mise en recouvrement (61 € avant crédits) est appliqué.

Code : `m4_population.py`, `m4_openfisca.py`, test `validation_M4.py`. Chaque simulation OpenFisca tourne dans un processus séparé (environ 3 Go pour 2 % des ménages). Un test complet dure environ 20 minutes.

## Validation (`resultats/validation_M4.md`, version 1.3, η = 0,8)

| Contrôle | Modèle | Référence | Statut |
|---|---|---|---|
| Personnes, ménages | 66,38 M ; 30,97 M | 66,3 M ; 30,9 M (Insee) | conforme |
| Foyers fiscaux | 38,3 M | 41,6 M (DGFiP) | −7 % : communautés hors champ, rattachements simplifiés |
| Parts par foyer, déciles 4 à 10 de revenu par part | 1,51 à 1,71 | 1,55 à 1,70 | conforme ; déciles 2 et 3 : ±15 % |
| **Impôt au barème par part, déciles 6 à 8** (test) | 266 ; 660 ; 1 285 € | 300 ; 710 ; 1 290 € | conforme |
| **Impôt au barème par part, déciles 9 et 10** (test) | 2 680 ; 10 738 € | 2 510 ; 10 050 € | +7 % chacun |
| **Impôt au barème total** (test) | 100,5 Md€ (99,2 à 102,0 selon η) | ≈ 98,6 Md€ | **+2 %** |
| Part de foyers imposés par tranche de revenu fiscal (test) | 1 % ; 37 % ; 56 % ; 71 % ; 94 % | 3 % ; 29 % ; 61 % ; 72 % ; 91 % | conforme à ±8 points |
| Impôt net par tranche (test partiel : prélèvement forfaitaire et réductions calés) | de −15 % (30-50 k€) à +10 % (100-200 k€) | IRCOM | acceptable |
| Impôt net total | 92,4 Md€ (91,1 à 93,9 selon η) | 91,7 Md€ | conforme, mais en partie par calage |
| Crédits d'impôt modélisés (emploi à domicile, garde) | ≈ 9,9 Md€ | ≈ 9,7 Md€ | conforme |

**Lecture.** La population reproduit l'impôt au barème à 2 % près au total et décile par décile. Le barème n'a servi à aucun calage, ce qui valide la combinaison structure familiale × revenu × législation.

Ce qui reste fragile :
- Le niveau de l'impôt net dépend de deux calages : le capital par décile et les réductions et crédits non modélisés.
- Le poste « exonéré » est un solde (57 Md€). Sa composition (revenus étrangers, plus-values en report, revenus exonérés) n'est pas identifiée.

Conséquence pour l'usage : une réforme du barème, du quotient familial ou de la décote peut être chiffrée. Une réforme de l'imposition du capital ou des niches fiscales exige d'abord de modéliser ces postes un à un.

## Prestations (version 1, `m4_prestations.py`, test `validation_prestations.py`)

**Méthode**
- **Familles au sens de la CAF** : un couple (marié, pacsé ou en concubinage) et ses enfants de moins de 25 ans vivant au foyer.
- **Ressources** : les montants annuels de M4 (salaires, chômage, pensions) sont répartis uniformément sur les mois, avec des coefficients approchés pour passer au net. Les revenus N-1 et N-2 reprennent les mêmes montants.
- **Logement** :
  - le statut d'occupation vient du recensement ;
  - le loyer est imputé (surface × prix au m² : parc social 6,5 € ; privé 21 / 13 / 10 € selon la zone ; meublé +15 %) ;
  - la zone APL est approchée par le département.

  Hypothèses de niveau D.
- **Calcul** : OpenFisca, mois d'octobre 2024 multiplié par 12, sur un sous-échantillon de 0,5 % des ménages (contrainte de mémoire).
- **Grandeur obtenue** : des droits, avec un recours de 100 %. Le rapport entre montant versé et montant simulé est un taux de recours apparent, à comparer aux estimations de non-recours de la DREES.

**Résultats (`resultats/validation_prestations.md`)**

| Prestation | Éligibles simulés | Bénéficiaires réels | Droits simulés | Versé | Recours apparent (foyers ; masse) | Estimation DREES du recours | Lecture |
|---|---|---|---|---|---|---|---|
| RSA | 2,90 M | 1,83 M | 15,4 Md€ | 11,9 Md€ | 63 % ; 77 % | 63 à 67 % des foyers | cohérent |
| Prime d'activité | 6,25 M | ≈ 4,55 M | 15,0 Md€ | ≈ 10,3 Md€ | 73 % ; 69 % | ≈ 50 % des foyers, 54 à 57 % de la masse | éligibles sous-estimés d'environ 25 % |
| Allocations familiales | 4,77 M | 4,7 M | 14,0 Md€ | — | 99 % | recours quasi complet | conforme |
| Aides au logement | 5,25 M | ≈ 5,8 M | 14,4 Md€ | ≈ 16 Md€ | 110 % ; 111 % | recours élevé | droits sous-estimés d'environ 10 % |

**Écarts et causes probables**
- **Prime d'activité** : les revenus lissés sur l'année suppriment les trimestres à faibles revenus (contrats courts, intérim). Or l'éligibilité se joue trimestre par trimestre.
- **Aides au logement** :
  - les étudiants en résidence universitaire et en foyer (communautés) sont hors champ ;
  - les loyers et les zones sont imputés grossièrement.
- **Non modélisés** : allocation aux adultes handicapés (le recensement n'a pas d'information sur le handicap), revenus du patrimoine dans les bases de ressources, non-recours.

## Travaux restants
1. **Postes calés à modéliser un à un** : réductions et crédits (investissement locatif, souscriptions, dépendance, d'après le tableau DGFiP par décile et par dispositif) ; option pour le barème (2,5 M de foyers, abattement de 40 % sur les dividendes) ; composition du poste exonéré.
2. **Écart de 3 M de foyers** : population des communautés (fichier détail, catégorie 1), rattachement des jeunes adultes.
3. **Prestations** : non-recours explicite (taux DREES appliqués par tirage, pour que le simulateur rende des montants versés) ; variabilité infra-annuelle des revenus pour la prime d'activité ; loyers à partir de sources publiques par zone ; allocation aux adultes handicapés.
4. **Recalage 2022 → année courante** sur M1 (âge, sexe) et sur l'évolution des revenus.
