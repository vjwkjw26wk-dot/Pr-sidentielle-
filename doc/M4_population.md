# Module M4 — Population de ménages et de foyers fiscaux (version 1)

**Statut : en partie construit (16 novembre 2026).** La structure des ménages est validée. Le test sur l'impôt sur le revenu encadre la valeur publiée sans la reproduire, et la composition des revenus autres que salaires et pensions reste inconnue.

## Base : de vrais ménages, pas une population inventée
Le fichier détail du recensement 2022 (Insee, « Individus localisés à la région », licence ouverte, 17,5 millions d'individus pondérés) contient des ménages réels anonymisés : identifiant de ménage, lien à la personne de référence, famille, âge, sexe, statut conjugal, activité, statut salarié ou non, groupe socioprofessionnel, temps partiel, études. La structure familiale n'est donc pas reconstruite à partir de marges (révision de la décision A4).

Échantillon de travail : tirage aléatoire de 2 % des ménages ordinaires (163 826 ménages, 344 527 personnes, 201 821 foyers), poids = poids Insee / 0,02. Le taux est un paramètre ; 2 % suffit pour les masses nationales et tient en mémoire avec OpenFisca (environ 3 Go, 90 s par calcul).

## Foyers fiscaux (règles de la version 1)
- Les adultes d'une même famille mariés ou pacsés forment un foyer commun ; les concubins déclarent séparément.
- Un enfant de la famille est rattaché s'il a moins de 18 ans, ou moins de 25 ans et fait des études ; il l'est au premier adulte de la famille (le plus âgé, pour des concubins).
- Toute autre personne forme son propre foyer ; un parent isolé avec personne à charge reçoit la case T.

## Revenus : rang tiré des caractéristiques, niveau tiré de la DGFiP
1. **Score latent** par adulte, pour l'ordre seulement. Pour un salarié, il part du salaire net moyen en équivalent temps plein 2024 selon le groupe socioprofessionnel et le sexe (Insee), corrigé du temps partiel et d'un profil d'âge, avec une dispersion log-normale. Pour un retraité, il part de la pension moyenne de droit direct selon le sexe, plus la réversion des veuves (DREES, 2023). Les indépendants, chômeurs et autres inactifs reçoivent des grilles forfaitaires (hypothèses, niveau D).
2. **Revenu fiscal de référence** : les foyers, classés par score, reçoivent le revenu fiscal de leur rang dans la distribution DGFiP (IRCOM 2025, revenus 2024, 25 tranches). La densité est linéaire dans chaque tranche, avec la moyenne publiée ; la dernière tranche est une loi de Pareto.
3. **Salaires et pensions déclarés** : rapports publiés salaires / revenu fiscal et pensions / revenu fiscal par tranche, partage selon la composition du foyer, puis calage des montants moyens par foyer de chaque tranche.
4. **Autres revenus** = revenu fiscal visé − revenu fiscal issu des salaires et pensions. Leur composition est inconnue (voir limites).

Code : `code/src/m4_population.py`, couplage OpenFisca `code/src/m4_openfisca.py`, test `code/tests/validation_M4.py`.

## Validation (`resultats/validation_M4.md`)

**Structure** : 66,38 M de personnes et 30,97 M de ménages, contre 66,3 M et 30,9 M publiés par l'Insee pour 2022.

**Foyers** : 38,3 M contre 41,6 M à la DGFiP, dont 0,3 M de non-résidents, soit 3,0 M de moins (−7 %). Trois causes :
- le champ exclut les communautés (maisons de retraite, internats, foyers), qui déclarent pourtant ;
- les règles de rattachement sont simplifiées ;
- un mariage, un divorce ou un décès donne deux déclarations dans l'année.

Les montants sont donc calés en moyenne par foyer, et les masses ramenées au nombre de foyers DGFiP pour les comparaisons.

**Test sur l'impôt sur le revenu 2024 (OpenFisca-France)**, grandeur non utilisée pour construire la population. L'impôt est pris au sens de l'IRCOM : barème, contribution sur les hauts revenus, prélèvement forfaitaire, seuils de recouvrement.

| Variante pour les « autres revenus » | Impôt modèle avant réductions et crédits |
|---|---|
| V0 : non imposables | 82,2 Md€ |
| V1 : revenus de capitaux au prélèvement forfaitaire | 113,1 Md€ (dont 29,1 Md€ de prélèvement forfaitaire) |
| V2 : imposés au barème | 155,4 Md€ |
| DGFiP, impôt net après réductions et crédits | 91,7 Md€ ; avant crédits, au moins 101 Md€ (crédits ≈ 9,7 Md€) |

Ce qui est conforme :
- **Part de foyers imposés par tranche (V0)** : 1 %, 41 %, 62 %, 74 %, 94 %, 100 % contre 3 %, 29 %, 61 %, 72 %, 91 %, 97 % publiés, de moins de 15 000 € à 200 000 € de revenu fiscal. La combinaison structure familiale × revenu × barème fonctionne.
- **Hauts revenus (V1)** : 16,8 Md€ contre 18,5 Md€ entre 200 000 € et 1 M€ ; 9,8 Md€ contre 10,1 Md€ au-delà de 1 M€.

Ce qui ne l'est pas encore :
- **Tranches moyennes** : même en V0, l'impôt dépasse l'impôt net de 15 % entre 30 000 € et 100 000 €. C'est l'ordre de grandeur des réductions et crédits, absents du modèle, mais la part qui leur revient n'est pas démontrée. Les salaires IRCOM incluent aussi des montants exonérés (heures supplémentaires, prime de partage de la valeur).
- **Variante V1 sous 50 000 €** : le prélèvement forfaitaire porte sur un « reste » qui n'est pas du capital, et rend imposés 61 à 77 % des foyers modestes. Le prélèvement simulé (29 Md€) dépasse de loin le rendement possible sur les 61 Md€ de revenus du capital déclarés.

**Conclusion** : la population convient pour la structure des ménages et la progressivité de l'impôt. Elle n'est pas encore utilisable pour chiffrer une réforme de l'impôt sur le revenu au milliard près.

## Travaux restants, par ordre d'effet attendu
1. **Composition des autres revenus** : capitaux mobiliers, plus-values, revenus fonciers, revenus d'indépendants, revenus exonérés inclus dans le revenu fiscal. Source : statistiques nationales DGFiP par case de déclaration (data.economie.gouv.fr, injoignable depuis l'environnement le 16 novembre 2026) et statistiques par décile de revenu fiscal par part (impots.gouv.fr).
2. **Réductions et crédits d'impôt** : imputer les principaux (emploi à domicile, garde d'enfants, dons) sur les fréquences et montants moyens publiés par la DGFiP.
3. **Écart de 3 M de foyers** : intégrer la population des communautés (fichier détail, catégorie 1) et affiner le rattachement des jeunes adultes.
4. **Prestations** (RSA, prime d'activité, allocations familiales, aides au logement) : calcul OpenFisca et comparaison aux masses publiées par la CNAF ; demande d'ajouter les loyers (disponibles dans le fichier détail des logements).
5. Projection 2022 → année courante : recalage sur M1 (âge, sexe) et sur l'évolution des revenus.
