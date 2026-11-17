# M10 — Couplage de la microsimulation des ménages et du modèle bouclé (version 0.1)

**État : le sens micro → macro est construit et testé.** Une réforme de l'impôt sur le revenu ou des prestations est
calculée ménage par ménage par OpenFisca, puis ses montants entrent dans le modèle bouclé M8. Le sens macro → micro
n'est pas fait : les revenus de M4 ne sont pas encore revalorisés avec les salaires, l'emploi et les prix simulés par M8.
Code : `src/m10_couplage.py`, `src/m4_openfisca.py` (réformes paramétriques), `src/m8_modele.py`
(`Exogenes.mesure_menages`). Test : `tests/validation_M10.py`. Rapport : `resultats/validation_M10.md`.

## 1. Chaîne de calcul

1. **Réforme.** Elle est décrite par une liste de paramètres OpenFisca modifiés, en valeur absolue ou par un facteur, à
   partir d'une date. Exemples : taux et seuils du barème, décote, plafond du quotient familial, montant du RSA, de la
   prime d'activité, des allocations familiales.
2. **Calcul ménage par ménage**, en législation actuelle puis après réforme, sans changement de comportement :
   - impôt sur le revenu sur 2 % des ménages, avec la chaîne validée de M4 (mêmes imputations ; réductions et crédits
     non modélisés repris de la législation actuelle) ;
   - prestations sur deux sous-échantillons de 0,5 %.
   Chaque calcul tourne dans un processus séparé, à cause des contraintes de mémoire.
3. **Montants versés.**
   - L'impôt est ramené aux 41,6 millions de foyers de la DGFiP.
   - Les prestations sont multipliées par le taux de recours apparent en masse mesuré en législation actuelle : RSA 0,68 ;
     prime d'activité 0,66 ; allocations familiales et aides au logement 1.
4. **Effets distributifs.** Ils sont calculés par décile de niveau de vie, approché par le revenu fiscal de référence des
   foyers du ménage, moins l'impôt, plus les prestations, rapporté aux unités de consommation (échelle de l'OCDE
   modifiée).
5. **Passage au modèle bouclé.** Les variations d'impôt et de prestations, en M€ de revenus 2024, sont indexées sur le
   PIB nominal simulé. Elles modifient le revenu disponible des ménages et les comptes publics, puis tout le bouclage :
   consommation, production, emploi, prix, recettes.

Temps de calcul : environ 6 minutes pour la législation actuelle (mise en cache), puis 1 à 5 minutes par réforme.

## 2. Validation

| Réforme | Effet statique | Repère externe | Lecture |
|---|---|---|---|
| Législation actuelle | Impôt net 92,4 Md€ | 91,7 Md€ (DGFiP) | conforme |
| Barème non revalorisé (seuils, décote, plafond du quotient familial −2 %) | +2,7 Md€ | ≈ 4 Md€ pour 2,1 % (projet de loi de finances pour 2027) ; 1,9 Md€ pour le gel de 2026, face à 0,9 % d'inflation (Bercy, Haut Conseil des finances publiques) ; calcul direct à partir de la répartition des foyers par taux marginal ≈ 3,2 Md€ | écart d'environ 30 % aux chiffrages officiels, ramené à environ 15 % après correction des différences de champ (voir ci-dessous) |
| Première tranche de 11 % à 14 % | +13,6 Md€ | ordre de grandeur cohérent : la baisse de 14 % à 11 % de 2020 avait été chiffrée à 5 Md€, mais elle était partiellement compensée par un abaissement du seuil de la tranche à 30 % | à confirmer |
| RSA +10 % | droits +2,8 Md€ ; versé +1,9 Md€ | ≈ 10 % de 11,9 Md€ versés = 1,2 Md€ à recours constant, davantage avec les nouveaux éligibles | plausible, un peu élevé (RSA déjà surestimé de 8 % en nombre) |

**Sensibilité aux seuils : diagnostic (17 novembre 2026).**
- **Répartition des foyers par taux marginal d'imposition.** Elle est reproduite :

  | | 0 % | 11 % | 30 % | 41 % | 45 % |
  |---|---|---|---|---|---|
  | M4 (M de foyers) | 13,6 | 20,8 | 6,8 | 0,40 | 0,08 |
  | DGFiP (M de foyers) | 13,5 | 20,7 | 6,4 | 0,42 | 0,06 |

  La densité des foyers par tranche de revenu fiscal est, elle, calée par construction sur l'IRCOM.
- **Calcul direct.** À partir de cette répartition, le calcul donne environ 3,2 Md€ pour −2 %. M4 donne 2,7 Md€, soit −15 %. L'écart restant vient des interactions entre la décote et le plafonnement du quotient familial, que le calcul direct ignore.
- **Différences de champ avec les chiffrages officiels**, qui expliquent le reste de l'écart :
  - revenus 2025-2026, plus élevés de 5 à 8 % que les revenus 2024 de M4 ;
  - autres paramètres indexés avec le barème (abattements de 10 % sur les salaires et les pensions, seuils divers) ;
  - 3 millions de foyers absents du champ.
- **Conclusion.** Pas de biais structurel identifié dans la population. Les chiffrages de réformes du barème sont à lire avec une marge d'environ −15 %. Aucune correction ad hoc n'est appliquée.

C'est la première vérification de la *sensibilité* de M4 à une réforme. Jusqu'ici, seul le *niveau* de l'impôt avait été
validé.

**Effets macroéconomiques.** Exemple : la hausse de la première tranche (+13,6 Md€, soit 0,5 point de PIB).
- La consommation baisse de 0,7 % et le PIB de 0,09 % la première année.
- Le solde public s'améliore de 0,32 point de PIB : environ un tiers du gain statique est perdu par le bouclage.
- L'effet sur le PIB s'efface à moyen terme sous l'effet de la fermeture d'offre (décision A12).

## 3. Limites

- **Effets statiques** : pas de réaction de l'offre de travail, du recours aux prestations ni de l'optimisation fiscale à la réforme.
- **Niveau de vie** : approché (revenu fiscal de référence, avant CSG, hors revenus exonérés). Ce n'est pas le revenu disponible de l'Insee.
- **Revenus et ménages de 2024** : les revenus ne sont pas revalorisés par M8 ; le montant statique est indexé sur le PIB nominal.
- **Prestations** : erreur d'échantillonnage d'environ 2 % ; les petites réformes de prestations sont imprécises.
- **Prélèvements non couverts** : CSG, CRDS, cotisations des salariés et taxe foncière ne passent pas encore par M4. Dans M8, ils restent à taux apparents.

## 4. Suite

1. Sens macro → micro : revaloriser les salaires et pensions de M4, et repondérer l'emploi, avec les trajectoires de M8.
2. CSG et cotisations des salariés dans M4. OpenFisca les calcule, mais les salaires bruts doivent être reconstitués.
3. Revaloriser avec le barème l'ensemble des paramètres indexés (abattements, seuils), pour reproduire exactement le périmètre des chiffrages officiels.
