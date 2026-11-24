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

Effets centraux sous R2 + BCE + prime (20 ans) : S1 +0,23 % de PIB / +23,4 pt de dette ; S2 +2,28 / +32,1 ;
S3 +4,99 / +52,4 ; S4 −0,94 / −43,6 ; S5 +1,30 / +13,4. L'endogénéité des taux amplifie les effets sur la dette
(prime souveraine et charge d'intérêts), beaucoup moins ceux sur le PIB.

| Paramètre | PIB (pt de %) | dette (pt de PIB) | stratégie la plus sensible | classements |
|---|---|---|---|---|
| prime_solde (0 / −0,118) | 0,01 | 7,63 | S3 | inchangés |
| prime_dette (0,007 / 0,03) | 0,02 | 7,09 | S3 | inchangés |
| bce_activite (0,1 / 0,5) | 0,13 | 6,47 | S3 | inchangés |
| bund_transmission (0,2 / 0,6) | 0,00 | 2,32 | S3 | inchangés |
| entreprises_vitesse (0,6 / 1,0) | 0,08 | 0,69 | S3 | inchangés |
| bce_inflation (0,2 / 0,6) | 0,00 | 0,27 | S5 | inchangés |
| menages_vitesse (0,25 / 0,6) | 0,00 | 0,13 | S3 | inchangés |

Les paramètres de prime souveraine sont les plus influents sur la dette des stratégies déficitaires ; ils restent
au second rang derrière le choix du régime monétaire lui-même (taux exogènes ou BCE + prime : jusqu'à 15 points de
dette pour S3).

Lecture : à l'horizon de 20 ans, les effets des stratégies sont beaucoup plus sensibles au régime (règle budgétaire,
politique monétaire, fermeture, ancrage) qu'aux paramètres structurels testés ici. Les paramètres de comportement
déplacent la dette de moins de 1,5 point de PIB ; les paramètres monétaires (sous régime BCE) jusqu'à 7,6 points pour
la stratégie la plus déficitaire. Aucun ne modifie les classements en PIB ou en dette.

## 3. Environnements calibrés : σ = 0,3 et 0,6, équation de prix v0.9

Chaque environnement est calibré une fois (référence recalée sur les mêmes cibles), puis S1-S5 sont évalués sous le
régime principal :

Références (2047) : dette 273,8 % du PIB (σ = 0,45), 275,4 % (σ = 0,3), 268,8 % (σ = 0,6) ; mêmes cibles de calage
(chômage 7,0 % en 2047). Durée de calibration : environ 100 minutes chacune en parallèle (≈ 50 minutes de calcul).

Effets à 20 ans (année 2046), régime principal :

| Stratégie | PIB σ 0,3 / 0,45 / 0,6 (%) | dette σ 0,3 / 0,45 / 0,6 (pt) | emploi σ 0,3 / 0,45 / 0,6 (milliers) | chômage σ 0,3 / 0,45 / 0,6 (pt) |
|---|---|---|---|---|
| S1 | 0,36 / 0,32 / 0,30 | 17,1 / 16,9 / 17,0 | 167 / 179 / 206 | 0,04 / 0,01 / −0,07 |
| S2 | 2,37 / 2,39 / 2,40 | 23,0 / 24,2 / 26,4 | 153 / 103 / 41 | 0,00 / 0,15 / 0,33 |
| S3 | 5,21 / 5,19 / 5,17 | 35,0 / 37,8 / 42,1 | 845 / 759 / 637 | 1,14 / 1,38 / 1,73 |
| S4 | −0,95 / −1,00 / −1,03 | −37,8 / −38,5 / −39,4 | −38 / −14 / +19 | 0,11 / 0,04 / −0,06 |
| S5 | 1,37 / 1,33 / 1,31 | 10,6 / 11,2 / 12,4 | −58 / −92 / −130 | 0,50 / 0,60 / 0,71 |

Lecture : σ ne change presque pas les effets sur le PIB (≤ 0,05 point) ni les classements en PIB et en dette ; il agit
sur le contenu en emplois des stratégies (substitution capital-travail) et, par là, sur la dette (jusqu'à 7 points
pour S3). Les signes de l'emploi de S4 et du chômage de S1 et S4 changent avec σ : ce sont les mêmes cas non robustes
que dans le tableau des régimes.

**Équation des prix de VA v0.9** (environnement `p4_prix_v09`, calibré en 45 minutes ; référence : dette 267,3 % du
PIB en 2047) comparée à l'équation de frontière de P4, à 20 ans :

| Stratégie | PIB P4 / prix v0.9 (%) | dette (pt) | prix (%) | emploi (milliers) |
|---|---|---|---|---|
| S1 | 0,32 / 0,28 | 16,9 / 14,3 | 0,71 / 0,99 | 179 / 203 |
| S2 | 2,39 / 2,40 | 24,2 / 23,9 | −1,03 / −1,12 | 103 / 104 |
| S3 | 5,19 / 5,23 | 37,8 / 38,3 | −1,85 / −1,90 | 759 / 758 |
| S4 | −1,00 / −1,05 | −38,5 / −39,7 | 0,29 / 0,37 | −14 / −1 |
| S5 | 1,33 / 1,33 | 11,2 / 9,3 | −1,67 / −1,72 | −92 / −77 |

Lecture : chaque équation de prix étant évaluée avec son propre environnement calibré, les écarts sont faibles
(≤ 0,05 point de PIB, ≤ 2,6 points de dette, surtout pour S1 dont les effets passent par les prix). Les classements
sont identiques. P4 (frontière) reste la configuration de travail ; l'équation v0.9 est une variante disponible.

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
