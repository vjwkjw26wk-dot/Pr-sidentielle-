# 19 — Modèle v0.8 : corrections, estimations et nouveaux modules (phase 3.1)

Ce document décrit les changements de la v0.8 par rapport à la v0.7 ; l'audit qui les motive est le document 18, le
registre des paramètres le document 20. La v0.7 reste disponible dans l'historique Git (commit 09b284b).

## 1. Défaut de code corrigé

Le terme proportionnel de la fermeture écrasait l'amortissement du point fixe (§ 0 du document 18). Variable
renommée ; test de non-régression `test_amortissement_du_point_fixe_independant_de_la_fermeture`.

## 2. Fermeture : spécification et estimation

### 2.1 Spécification retenue

    Z_t = Z_{t−1} − ρ g_{t−1} − a (g_{t−1} − g_{t−2}) + θ (ln Y*_{t−1} − ln Y*ref_{t−1})

avec **a = 0** (au lieu de 0,3), **μ = 0** (effet des tensions sur les importations, au lieu de 0,3), **ρ = 0,2** (au lieu
de 0,15), **θ = 0,75** (au lieu de 1,5).

Pourquoi a = 0 et μ = 0. Les réponses impulsionnelles du modèle (`phase31/irf_fermeture.py`) montrent que, une fois le
défaut de code corrigé, ces deux termes en différence produisent des oscillations de période deux ans après tout choc
ponctuel (demande ou offre). Les écarts de production observés (AMECO, FMI) n'oscillent pas : leur dynamique est celle
d'un AR(2) à racines réelles (φ₁ ≈ 1,0-1,1 ; φ₂ ≈ −0,3 à −0,4). Aucun des deux termes n'est estimé ; ils sont retirés
de la spécification centrale (μ reste disponible en sensibilité).

### 2.2 Estimation de ρ et θ

Données d'étalonnage : écart de production de la Commission européenne (AMECO, AVGDGP) et du FMI (WEO, NGAP_NPGDP),
France, 1982-2019 (crise sanitaire exclue). Données de validation : le backtest (§ 5), non utilisé pour ce choix.

1. **Ce que les données identifient.** La durée moyenne d'un écart de production (somme de la réponse de l'AR(2) à un
   écart initial de 1, sur dix ans) : 2,8 ans (AMECO ; intervalle bootstrap à 90 % : 2,0-5,3) et 2,3 ans (FMI ;
   1,6-4,0).
2. **Ce qu'elles n'identifient pas.** La régression de l'écart sur la croissance du potentiel donne un coefficient
   contemporain positif (AMECO : +3,0, écart-type 1,0), à l'opposé de ce qu'implique un retard de la production sur le
   potentiel : le potentiel publié est obtenu en partie par filtrage de la production elle-même (simultanéité). Ce
   moment n'est pas utilisé.
3. **Spécifications testées.** Asymétrie (expansion / contraction) : t = 0,03 (AMECO), −0,47 (FMI) ; dépendance à l'état
   (croissance du potentiel × écart passé) : t = 1,4 et 1,5. Aucune n'est significative : spécification linéaire
   unique, constante dans le temps. La stabilité entre 1982-1999 et 2000-2019 n'est pas rejetée pour φ, mais les
   coefficients β changent beaucoup (instabilité du potentiel publié).
4. **Moment du modèle.** Durée de l'écart de production après un choc d'offre permanent (productivité −1 % en 2028),
   calculée pour une grille ρ ∈ {0,1 ; 0,2 ; 0,3}, θ ∈ {0 ; 0,5 ; 0,75 ; 1,0 ; 1,5}, a ∈ {0 ; 0,15}.
5. **Contraintes.** Durée dans l'union des intervalles à 90 % (1,6-5,3 ans) ; pas de dépassement de plus de 10 % de
   l'écart initial ; θ compatible avec un ancrage microéconomique : réponse de la consommation à un choc permanent de
   revenu d'environ 0,6-0,65 (Blundell, Pistaferri, Preston 2008) et de l'investissement proche de 1, soit θ entre 0,4
   et 1,0 en part de la demande.
6. **Résultat.** Configurations plausibles : (ρ, θ) ∈ {(0,1 ; 1,0), (0,2 ; 0,5), (0,2 ; 0,75), (0,2 ; 1,0), (0,3 ; 0,5),
   (0,3 ; 1,0)}. Valeur centrale (0,2 ; 0,75), durée 3,0 ans. θ = 1,5 (v0.7) est rejeté (dépassement de 20 à 30 %),
   θ = 0 l'est aussi (durées de 4,6 à 7,2 ans).
7. **Effet sur l'incertitude.** Dette en 2047 après le choc d'offre de −1 % : de −12 à +10 points sur toute la grille,
   de −6 à +6 points sur l'ensemble plausible.

La part du capital dans l'anticipation (`PART_K_ANTICIPATION`) n'est pas identifiable sur ces données : elle est
maintenue à 1 (comme en v0.7) et testée à 0 (incertitude de structure).

## 3. Incidence économique des prélèvements sur les entreprises

La part de chaque prélèvement supportée à long terme par les salariés déplace la **cible de long terme du coût salarial**
de l'équation de salaires (terme `ancre_salaire`) ; la correction d'erreur donne la dynamique. Le reste est supporté par
les actionnaires (profits, dividendes, investissement) et, pour les impôts de production, par les consommateurs (prix).

| Prélèvement | Part sur les salaires (basse / centrale / haute) | Consommateurs | Source |
|---|---|---|---|
| IS | 0 / 0,3 / 0,5 | (indirect) | Fuest, Peichl, Siegloch (AER 2018) : ≈ 0,5 pour l'impôt local allemand |
| Impôts de production | 0 / 0,2 / 0,4 | 0,5 | Pas d'estimation causale française sur les salaires [H] |
| Cotisations employeurs | 1 / 0,5 / 0,2 (part transmise aux salaires) | (indirect) | Bozio, Breda, Grenet (2019) ; CICE : Carbonnier et al. (2019) |

En v0.7, la correction d'erreur des salaires transmettait implicitement la totalité des variations de cotisations aux
salaires à long terme (valeur 1) et aucune part de l'IS.

## 4. Distribution dynamique (M16)

Voir l'en-tête de `src/m16_distribution_dynamique.py` : méthode hybride sur les ménages de la microsimulation, huit
canaux sans double compte, effets d'emploi en espérance, contrôle de cohérence avec le revenu disponible
macroéconomique, horizons 2027, 2030, 2035, 2040, 2047. Groupes : décile, âge, statut (salarié, indépendant,
retraité, chômeur, inactif), catégorie sociale, configuration familiale, statut d'occupation du logement.

### 4.1 Corrections apportées pendant la réoptimisation (vérification des gagnants et des perdants)

La réoptimisation avec critères distributifs dynamiques a fait apparaître des résultats suspects (le relèvement de
l'âge légal augmentait le niveau de vie du premier décile de 9 % en 2047). Diagnostic et corrections :

1. **Réforme de l'âge légal.** Les actifs seniors supplémentaires (M9) étaient traités comme des entrées d'inactifs
   d'âge actif (surtout dans le premier décile) et la hausse du chômage comme des pertes d'emploi de salariés. Ils sont
   désormais attribués aux ménages dont la personne de référence a 58 à 67 ans, en pseudo-cohorte : salaire maintenu
   pour les ménages ayant des actifs occupés, allocation chômage pour les entrées au chômage, pension non versée au
   prorata des pensions perçues. Résultat : le premier décile perd (−1 % en 2047 pour 65 ans), les ménages de 60-74
   ans dont un membre travaille gagnent, les retraités et les jeunes perdent ; résiduel de cohérence 0,03 point au lieu
   de 0,48.
2. **Mesures sans équivalent dans la microsimulation** : baisse des allocations chômage (répartie au prorata du nombre
   de chômeurs), transferts aux ménages (au prorata des prestations), point d'indice (au prorata des salaires, faute
   d'identifier les agents publics ; masse indiciaire nette ≈ 187 Md€). Montants convertis en part du revenu
   disponible macroéconomique de 2025. Exemple : allocations chômage −25 % → premier décile −3,4 %, dixième −0,25 %.
3. **Contrôle de cohérence** : la comparaison se fait désormais en termes réels (la TVA réduit le revenu réel par les
   prix dans le compte macroéconomique, par le canal direct dans la microsimulation) et hors droits de succession
   (transferts en capital, absents du revenu disponible). Le résiduel nominal reste publié (`residuel_nominal_pct`).

Toutes les expériences et stratégies ont été relancées après ces corrections ; les résultats antérieurs sont
conservés dans `phase31/resultats/avant_correction_m16/`.

## 5. Offre de travail (M15)

18 cas types (9 configurations familiales × locataire / propriétaire) au lieu de 5. Les propriétaires ne perçoivent
pas d'aide au logement : l'effet d'une baisse des aides au logement sur la participation passe de +72 000 à +22 000
personnes (−10 %).

## 6. Backtest

`phase31/backtest.py` (méthode décrite dans l'en-tête), `phase31/analyse_backtest.py`. Résultats : rapport v0.8,
chapitre 5.
