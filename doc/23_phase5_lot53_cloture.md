# 23 — Phase 5 : lot 5.3 et clôture de la phase (robustesse, environnements, comportements, régimes)

Scripts : `phase5/lot53_strategies.py`, `lot53_structurels.py`, `lot53_structurels_monetaires.py`,
`lot53_environnements.py`. Résultats : `phase5/resultats/lot53_*`. Tests : `tests/test_lot53.py`.

## 1. Robustesse de S1-S5 (10 régimes, horizons 5, 10, 20 ans)

Environnement P4, convention « part constante ». Contrôle du transfert des programmes (traduits sur l'environnement
historique, transférés par écarts) : écart nul (0,0). Effets au régime principal (R2 figé, taux exogènes, jeu
central), à 20 ans :

| Stratégie | PIB (%) | dette (pt de PIB) | chômage (pt) |
|---|---|---|---|
| S1 protection | +0,32 | +16,9 | +0,01 |
| S2 emploi | +2,39 | +24,2 | +0,15 |
| S3 productivité | +5,19 | +37,8 | +1,38 |
| S4 redressement | −1,00 | −38,5 | +0,04 |
| S5 global | +1,33 | +11,2 | +0,60 |

Ce qui est robuste aux dix régimes : le classement en PIB aux extrémités (S3 premier, S4 dernier) et le classement en
dette (S4 le plus favorable, S3 le moins favorable). Ce qui ne l'est pas : l'ordre de S1 et S5 en PIB, le classement
en chômage (sensible au régime actif symétrique et aux variantes de fermeture), certains signes d'emploi. Ces cas sont
signalés automatiquement (`lot53_synthese_S1_S5.csv`, colonne « signe robuste »).

## 2. Sensibilité aux paramètres structurels modifiables sans recalibration

Amplitude maximale de l'effet à 20 ans quand le paramètre passe de sa valeur basse à sa valeur haute (régime
principal ; tous S1-S5 confondus) :

| Paramètre | statut | PIB (pt de %) | dette (pt de PIB) | classements |
|---|---|---|---|---|
| PSI_CHOMAGE (épargne de précaution) | [C] | 0,02 | 0,55 | inchangés |
| PSI_TAUX (taux réel et consommation) | [C] | 0,02 | 0,14 | inchangés |
| SEMI_ELAST_IS (transfert de bénéfices) | [B] | 0,00 | 1,29 | inchangés |
| THETA_TRESORERIE | [C] | 0,01 | 0,73 | inchangés |
| mu_taux (taux apparent des SNF) | [E] | 0,00 | 0,02 | inchangés |
| div_lissage (dividendes) | [H] | 0,01 | 1,41 | inchangés |

Paramètres monétaires : la première passe les évaluait à taux exogènes, où ils n'agissent pas (effet nul par
construction, ce n'était pas un résultat) ; corrigé dans `sensibilite_structurelle` (évaluation sous R2 + BCE + prime)
et relancé :

{MON}

Lecture : à l'horizon de 20 ans, les effets des stratégies sont beaucoup plus sensibles au régime (règle budgétaire,
fermeture, ancrage) qu'aux paramètres structurels de comportement testés ici ; ceux-ci déplacent surtout la dette, de
moins de 1,5 point de PIB.

## 3. Environnements calibrés : σ = 0,3 et 0,6, équation de prix v0.9

Chaque environnement est calibré une fois (référence recalée sur les mêmes cibles), puis S1-S5 sont évalués sous le
régime principal :

{ENV}

## 4. Enrichissements comportementaux

| Domaine | Ajouté pendant la phase 5 | Statut |
|---|---|---|
| Ménages : taux | taux des crédits à l'habitat de M24 dans l'arbitrage consommation-épargne | [E] transmission, [C] ψ_r |
| Entreprises : financement | coût du crédit aux SNF de M24 dans le coût d'usage ; compte des sociétés (M21) | [E] |
| Investissement hors APU | mesure `investissement_hors_apu` (pôle public bancaire, entreprises publiques) : effet de demande sans coût pour le solde public, part subventionnée optionnelle | [H], lot 6 |
| Épargne retraite par capitalisation | canal existant (recettes publiques en moins sans effet de demande : cotisations réorientées vers une épargne obligatoire) ; documenté pour les programmes RN et Horizons | [H] |
| Paramètres structurels | 17 paramètres modifiables sans recalibration (`STRUCTURELS`), avec bas / central / haut | [E]/[C]/[H] |

Non ajoutés, faute de données ouvertes permettant de les estimer ou parce qu'ils exigeraient une recalibration sans
gain démontré : durée d'assurance et carrières longues dans M9 (priorité 1 de la liste du doc 26), effets de richesse
immobilière, distinction des produits énergétiques dans la TVA, durée d'indemnisation du chômage. Ils sont
hiérarchisés dans le doc 26 (section 10).

## 5. Décision sur le pas trimestriel

**Non retenu pour le rapport.** Motifs : (1) les mesures des programmes sont annuelles (lois de finances) et les
horizons d'analyse sont de 5, 10 et 20 ans ; (2) la seule information infra-annuelle des programmes (ordonnances de
juillet 2027, collectif budgétaire de l'été 2027) se traite par la date de première application (`Mesure.debut`) et,
si nécessaire, par une montée en charge au prorata de l'année ; (3) les équations trimestrielles disponibles (M20) ne
couvrent que les salaires et les prix de VA marchands, et leur généralisation demanderait une recalibration complète
sans amélioration démontrée de la comparaison ; (4) le critère d'acceptation du « jumeau annuel » (doc 22 §2.3) ne
serait pas un gain pour les questions posées. La compatibilité reste préservée (crochets de régime n'utilisant que
les périodes passées, dividendes et dette retardés).

## 6. Régimes stabilisés (valeurs par défaut pour le rapport)

| Élément | Défaut | Variantes systématiques |
|---|---|---|
| Environnement | P4, convention de dépense « part constante », base 2022, horizon 2047 | σ 0,3 / 0,6 ; équation de prix v0.9 |
| Règle budgétaire | R2 figé (α 0,5, β 0,02, d* 90 %, plafond 0,5, clause −1,5) | R0, R1, R2 actif, R2 actif symétrique |
| Politique monétaire | taux exogènes (référence Euribor observé) | BCE + prime souveraine en écart à la référence |
| Jeu de paramètres | central | ancrage faible / fort, fermeture lente / rapide / chômage |
| Variante institutionnelle (M26) | conforme | contentieux, tension |
| Programme = régime | — | pour les candidats qui annoncent une règle d'or et un objectif de déficit (RN, Horizons) : R1 ou R2 en mode actif, en complément de la lecture « mesures » |

Ces défauts sont documentés et paramétrables ; ils ne seront plus modifiés sans motif démontré.
