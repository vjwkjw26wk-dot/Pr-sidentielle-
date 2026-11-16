# Module M4 — Population de ménages et de foyers fiscaux (version 1.2)

**Statut : en partie construit (16 novembre 2026, soir).**
- Validé : structure des ménages ; impôt sur le revenu des 80 % de foyers les moins aisés.
- Pas encore validé : le haut de la distribution, où l'impôt au barème est surestimé de 9 à 21 %. Impôt net total : 101 Md€ contre 91,7 Md€ publiés.

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
6. **Dépenses ouvrant droit à crédits ou réductions** (emploi à domicile, garde d'enfants, dons) : nombres de foyers et montants nationaux reproduits. Les autres réductions et crédits (investissements locatifs, souscriptions, outre-mer…) sont calés par décile de revenu fiscal par part sur le tableau DGFiP. Ils sont alors des données d'entrée, et non un test.
7. **Impôt** : OpenFisca-France 177 (barème, quotient familial, décote, prélèvement forfaitaire unique, crédits et réductions modélisés). La contribution sur les hauts revenus est calculée directement sur le revenu fiscal, car sa variable OpenFisca dépasse la mémoire disponible.

Code : `m4_population.py`, `m4_openfisca.py`, test `validation_M4.py`. Chaque simulation OpenFisca tourne dans un processus séparé (environ 3 Go pour 2 % des ménages). Un test complet dure environ 20 minutes.

## Validation (`resultats/validation_M4.md`)

| Contrôle | Modèle | Référence | Statut |
|---|---|---|---|
| Personnes, ménages | 66,38 M ; 30,97 M | 66,3 M ; 30,9 M (Insee) | conforme |
| Foyers fiscaux | 38,3 M | 41,6 M (DGFiP) | −7 % : communautés hors champ, règles de rattachement simplifiées |
| Parts par foyer, déciles 2 à 10 de revenu par part | 1,51 à 2,01 | 1,55 à 1,86 | conforme sauf déciles 2 et 3 (±15 %) |
| Impôt au barème par part, déciles 5 à 8 | 32 ; 273 ; 673 ; 1 296 € | 60 ; 300 ; 710 ; 1 290 € | conforme (écarts de 3 à 30 €) |
| Impôt au barème par part, décile 9 | 2 726 € | 2 510 € | +9 % |
| Impôt au barème par part, décile 10 | 12 141 € | 10 050 € | **+21 %** |
| Impôt au barème total | 110,1 Md€ (106 à 114 selon η) | ≈ 98,6 Md€ | +12 % |
| Prélèvement forfaitaire par part, décile 10 | 1 129 € | 1 440 € | −22 % |
| Crédits d'impôt modélisés | 9,9 Md€ | ≈ 9,7 Md€ | conforme |
| Impôt net total | 101,2 Md€ (97,5 à 104,9 selon η) | 91,7 Md€ | +10 % |
| Impôt net, tranches de revenu fiscal ≤ 50 000 € | 14,6 Md€ | 16,0 Md€ | −9 % |

**Lecture.** Pour 80 % des foyers, la combinaison structure familiale × revenu × législation reproduit l'impôt publié, décile par décile. L'excès d'impôt est concentré dans le dernier décile. La composition des revenus des foyers aisés y est mal connue : le modèle leur attribue trop de revenus au barème et pas assez de capital au prélèvement forfaitaire (−22 %).

La part de foyers imposés est surestimée dans les tranches basses (23 % contre 3 % sous 15 000 €). Cela vient d'un prélèvement forfaitaire sur de petits revenus de capital trop dispersés vers le bas de la distribution.

## Travaux restants
1. **Haut de la distribution** : caler la répartition capital / barème / exonéré du dernier décile sur les montants de prélèvement forfaitaire par décile publiés par la DGFiP (tableau par décile, colonne « impôt forfaitaire »), qui fournissent une contrainte directe ; tenir compte de l'option pour le barème (2,5 M de foyers, abattement de 40 % sur les dividendes).
2. **Écart de 3 M de foyers** : population des communautés (fichier détail, catégorie 1), rattachement des jeunes adultes.
3. **Prestations** (RSA, prime d'activité, allocations familiales, aides au logement) : calcul OpenFisca et comparaison aux masses de la CNAF.
4. **Recalage 2022 → année courante** sur M1 (âge, sexe) et sur l'évolution des revenus.
