# 21 — Rapport de la phase 4 : modèle macroéconomique intégré

Branches : `phase34` (v0.9, phases 3.4 et 4.1), `phase42` (4.2, chantier A), `phase42a2` (A.2), `phase43` (4.3-4.4,
chantiers B, C et validation intégrée). La v0.8 (`main`) n'a pas été modifiée. La **v0.9 reste la configuration par
défaut** : tous les ajouts de la phase 4 sont derrière des interrupteurs (`SPEC`) dont la valeur par défaut reproduit la
v0.9 à 1e-6 près (tests de non-régression).

Plan :
1. Architecture implémentée
2. Équations et mécanismes retenus
3. Interactions entre les blocs et leur vérification
4. Estimation, calibration et justifications
5. Résultats des tests et simulations
6. Arbitrages et variantes écartées
7. Limites et paramètres incertains
8. Tableau des tests
9. Bilan de maturité
10. Recommandation sur la phase 5

---

## 1. Architecture implémentée

### 1.1 Modules

| Bloc | Module | Contenu | Phase |
|---|---|---|---|
| Comptes et tableaux entrées-sorties | M3, M5 | TES 64 produits, 25 branches marchandes, système de prix de Leontief | antérieure |
| Équations estimées | M7 | emploi, prix de VA, salaires, investissement, consommation, logement, exportations, importations, transmission des prix d'importation | antérieure, σ ré-estimable (3.4) |
| Cœur de simulation | M8 | résolution annuelle par point fixe, fermeture, finances publiques, comptes d'agents | v0.9 + interrupteurs 4.2-4.3 |
| Référence à politique inchangée | M8_reference | recalage 2023-2025, FMI 2026-2031, hypothèses COR | antérieure |
| Retraites, offre de travail | M9, M15 | pensions par génération, population active | antérieure |
| Hétérogénéité, microsimulation | M10, M14 | propensions par décile, couplage | antérieure |
| Dette publique par cohortes | M17 | cohortes d'émission, courbe, indexées, validation AFT | 3.4 |
| Prix | M18 | prix de production, prix de VA, frontière des prix de facteurs | 4.2 (A, A.2) |
| Salaires | M19 | équations W0-W6, SMIC et règle légale | 4.2 (A) |
| Système trimestriel | M20 | salaires et prix de VA trimestriels (marchand), Phillips | 4.2 (A.2) |
| **Compte des sociétés** | **M21** | intérêts, IS, dividendes, épargne, capacité de financement, dette des SNF | **4.3 (B)** |
| **Validation prédictive** | **M22** | millésimes FMI, exogènes ex ante, classement des variables | **4.3 (C)** |

### 1.2 Configurations

| Nom | Définition | Statut |
|---|---|---|
| v0.8 | `configurer_v08()` | référence historique immuable |
| v0.9 | `configurer_v09()` : CES en heures (σ = 0,45), potentiel CES marchand, non marchand par sous-branche, salaire public instrument, dette par cohortes, coût du travail net du CICE | **défaut reproductible** |
| T1 | v0.9 + `prix_va = "frontiere"` + `tension_prix = "aucune"` | candidate du bloc prix (A.2) |
| **P4** | T1 + `societes = "compte"` (`configurer_phase4()`) | **configuration candidate de fin de phase 4** |

Variantes conservées et activables : T0 (v0.9 sans effet de tension), T2 (T1 + rattrapage salarial 0,17), prix de VA
avec hausses des coûts intermédiaires (`ci_hausse`), équations de salaires M19 (`brut`, `cible_conso`,
`cible_conso_smic`), capacité au capital désiré, variantes du compte des sociétés (`Exogenes.variante_societes`).

### 1.3 Résolution

Chaque année est résolue par un point fixe amorti (au plus 60 itérations, amortissement 0,5, critère 1e-7) sur la
production, les salaires et le chômage. L'ordre de calcul dans l'année :
1. prix d'importation ;
2. salaires, prix de VA, prix de Leontief ;
3. emploi et investissement par branche ;
4. revenu disponible et demande finale ;
5. importations et production (Leontief).

Après convergence : potentiel et écart de production, puis finances publiques et compte des sociétés. Ces deux comptes
ne rétroagissent sur l'année qu'à travers des variables retardées : dividendes de l'exercice t − 1, dette de fin t − 1.
C'est cohérent avec le calendrier réel (les dividendes rémunèrent l'exercice précédent) et compatible avec un pas
trimestriel futur.

---

## 2. Équations et mécanismes retenus (configuration P4)

### 2.1 Offre, production, emploi (phases 3.4 et 4.1)

- **Emploi par branche** (25 branches marchandes) : demande de travail CES en heures, à production donnée,
  ln N = ln q − σ ln(c_h / p_va) − (1 − σ)(ln E + ln d). La tendance d'efficience est dérivée de la même condition sur
  8 ans. σ = 0,45, calibré (non identifié), variantes 0,3 et 0,6.
- **Emploi non marchand** par sous-branche (L68B, O, P, Q86, Q87-88) : volume de VA divisé par une productivité
  tendancielle propre.
- **Potentiel** : CES normalisée sur la VA marchande + VA non marchande ; anticipation du potentiel de référence en
  rétrosimulation.
- **Fermeture** (v0.8, estimée en phase 3.1) : un supplément de demande résorbe chaque année ρ = 0,2 de l'écart de
  production et réagit aux chocs d'offre (θ = 0,75). Elle représente les canaux non modélisés (politique monétaire,
  crédit, confiance).

### 2.2 Prix, salaires, marges (phase 4.2, chantiers A et A.2)

- **Prix de VA** (panel annuel de 25 branches) : correction d'erreur vers la frontière des prix de facteurs,
  ln p_va* = θ_b ln CSU + (1 − θ_b) ln (p_I K_{t−1} / q). θ_b est la part du travail de la branche (médiane 1997-2019) ;
  le capital est valorisé au prix de l'investissement. Dynamique de court terme : CSU et volume. Pente sur l'écart de
  production κ = 0,10 hors industrie (calibrée). Effet du TUC retiré (non significatif, source de dérive).
- **Prix de production et à la consommation** : système de Leontief (prix de VA, prix d'importation par produit avec
  transmission partielle θ estimée, impôts sur les produits).
- **Salaires** (équation v0.9) : indexation de court terme 0,39 sur les prix à la consommation ; correction d'erreur
  vers la part des salaires en prix de VA ; Phillips −0,004 par point d'écart de chômage (calibrée : non identifiée en
  annuel ni en trimestriel).
- **Coût du travail** = rémunérations nettes des subventions sur salaires (CICE 2013-2018) ; bascule de 2019 en baisse
  de cotisations.
- **Marges** : taux de marge des branches marchandes = 1 − coût du travail / VA, publié en sortie.

### 2.3 Demande

- **Consommation** : correction d'erreur sur le revenu disponible réel, épargne de précaution (variation du chômage) et
  taux réel (calibrés, M13), propensions par décile pour les mesures (M14).
- **Logement** : équation estimée sur le revenu disponible.
- **Investissement des branches** : accélérateur en correction d'erreur ; coût d'usage (IS, taux) en niveau avec
  convergence à la vitesse des branches.
- **Exportations** : demande mondiale et compétitivité-prix.
- **Importations** : demande pondérée par les contenus en importations, prix relatifs, tendance.

### 2.4 Compte des sociétés et revenus du capital (phase 4.3, chantier B)

Description complète : `phase43/NOTE_B.md`. Résumé :
- intérêts versés par les SNF = taux apparent × dette ; le taux apparent rejoint le taux de marché (0,77 court,
  0,23 long, transmission 1,29, écart 3,4 pt) à la vitesse 0,60 [E] ; intérêts reçus = 0,77 × intérêts versés [C] ;
- IS = taux apparent de base × résultat courant avant impôt × facteur fiscal ;
- dividendes distribués aux détenteurs finals = 0,36 × résultat après intérêts et IS de l'exercice précédent [C].
  Répartition : ménages 42 %, reste du monde 50 %, APU 8 % ;
- épargne brute et capacité de financement par identité ; dette des SNF = dette de base indexée sur le PIB nominal
  + 1,06 × cumul des écarts de besoin de financement [E] ;
- revenus de la propriété des ménages et RNB reconstruits à partir des dividendes ; les profits induits par les
  mesures passent par ce compte (double compte avec M14 supprimé).

### 2.5 Finances publiques

- Recettes : taux apparents sur leurs assiettes simulées (impôts sur les produits / consommation, impôts des ménages /
  revenus, cotisations / masse salariale, IS : voir 2.4) et autres recettes ∝ PIB nominal.
- Dépenses : rémunérations publiques (salaire public instrument × emploi non marchand), autres consommations en volume ×
  prix, prestations indexées sur les prix de l'année précédente, allocations chômage ∝ chômeurs, autres dépenses en part
  du PIB.
- Charge d'intérêts par cohortes (M17), avec boucle intra-annuelle sur le besoin de financement.

### 2.6 Extérieur et comptes d'agents

RNB = PIB + revenus primaires nets du reste du monde. Ceux-ci sont indexés sur le PIB nominal, diminués de l'écart des
dividendes versés aux non-résidents (M21). Sorties : solde extérieur approché, épargne et capacité de financement des
ménages.

---

## 3. Interactions entre les blocs et leur vérification

### 3.1 Boucles

| Boucle | Mécanisme | Vérification |
|---|---|---|
| prix-salaires-marges | salaires ← prix conso, chômage ; prix de VA ← CSU, coût du capital ; prix conso ← Leontief | ancrage (A.2) ; chocs salaire, énergie, coût du travail (§ 3.2) |
| consommation-épargne-investissement | revenu disponible ← salaires, prestations, impôts, dividendes ; investissement ← production, coût d'usage | chocs impôts, IS, taux |
| production-emploi-chômage | Leontief → production → emploi CES → chômage → salaires ; fermeture | Okun et identité chômage-emploi dans tous les chocs |
| finances publiques-dette | assiettes simulées, charge d'intérêts par cohortes | identité de la dette ; coûts ex post |
| extérieur-compétitivité | exportations ← prix relatifs ; importations ← demande, prix ; dividendes au reste du monde | chocs de demande mondiale, d'énergie |
| sociétés-ménages | EBE → résultat → dividendes (t + 1) → revenu des ménages → consommation ; besoin de financement → dette des SNF → intérêts | identités B8G, B9, D4 ménages ; chocs IS et taux |

### 3.2 Batterie de chocs d'intégration (projection 2027-2046)

Base : trajectoire de référence à politique inchangée 2023-2047 (base 2022, recalée sur 2023-2025, FMI 2026-2031),
reconstruite pour chaque configuration (`phase43/d0_reference.py`). Dix chocs permanents (sauf indication) en 2027 ;
écarts à la référence. Script : `phase43/d1_chocs_integration.py` ; tableaux complets dans
`phase43/resultats/d1_chocs_{v09,p4}.csv` (17 variables, 6 horizons).

Configuration P4, à 1 / 5 / 20 ans :

| Choc | PIB (%) | Emploi (milliers) | Prix conso (%) | Solde public (pt PIB) | Autres effets |
|---|---|---|---|---|---|
| Demande publique +1 pt de PIB | 1,25 / 0,78 / 0,20 | +344 / +367 / +133 | −0,15 / +0,84 / +1,95 | −0,26 / −0,04 / +0,21 | exportations −1,3 % à 20 ans |
| Impôts des ménages +1 pt de PIB | −0,67 / −0,59 / −0,23 | −62 / −141 / −48 | +0,16 / −0,16 / −0,46 | +0,64 / +0,53 / +0,97 | consommation −1,9 % |
| Impôts sur les produits +10 % | −0,47 / −0,34 / −0,11 | −43 / −94 / −35 | +1,36 / +1,68 / +1,34 | +1,46 / +1,53 / +2,76 | salaire réel −1,6 % à 20 ans |
| Coût du travail −2 % (allègement) | 0,29 / 0,21 / 0,00 | +25 / +106 / +81 | −0,79 / −1,12 / −0,90 | −0,74 / −0,76 / −1,57 | marge +0,45 pt à 5 ans |
| IS −5 points | 0,02 / 0,15 / 0,38 | +2 / +29 / +88 | 0 / 0 / +0,48 | −0,53 / −0,52 / −0,36 | FBCF +1,6 %, dividendes +5,1 %, dette SNF −5,2 pt à 20 ans |
| Taux d'intérêt +1 pt | −0,12 / −0,15 / −0,44 | −11 / −33 / −112 | +0,03 / −0,02 / −0,38 | −0,26 / −1,14 / −5,68 | FBCF −1,8 %, dividendes −1,9 % |
| Demande mondiale +5 % | 0,51 / 0,36 / −0,02 | +43 / +98 / −31 | −0,17 / +0,11 / +0,33 | +0,14 / +0,32 / +0,40 | exportations +3,2 à +3,6 % |
| Énergie importée +50 % | −0,95 / −1,58 / −0,47 | −86 / −368 / −121 | +2,39 / +6,30 / +5,38 | −0,50 / −2,11 / −4,18 | salaire réel −6,4 %, solde extérieur −5,0 pt à 20 ans |
| Productivité +1 % | 0,02 / 1,06 / 1,22 | −210 / −134 / −17 | −0,35 / −1,23 / −1,03 | −0,33 / −0,15 / −0,06 | emploi revenu à la référence |
| Salaires +2 % (1 an) | −0,04 / 0,00 / 0,03 | −2 / −47 / −22 | +0,73 / +0,87 / +0,41 | +0,39 / +0,30 / +0,44 | salaire réel +0,8 % à 20 ans |

**Contrôles automatiques : 76 sur 76 réussis pour P4 et 66 sur 66 pour la v0.9** (`d1_controles_*.csv`). Ils
vérifient :
- l'absence de valeur manquante ;
- la stabilité des écarts sur 2042-2046 (variation annuelle inférieure à 0,25 point) ;
- 36 signes attendus à 5 ans ;
- l'identité chômage-emploi (Δu = −Δemploi / population active, à 0,05 point près) ;
- les identités du compte des sociétés (moins de 1e-6 M€ ; 10 contrôles, P4 seulement).

Lecture par boucle :
- **Prix-salaires-marges.** Une baisse de 2 % du coût du travail fait baisser les prix à la consommation de 1,1 % à
  5 ans (56 %), le reste allant aux marges. Un
  choc salarial temporaire laisse un niveau de prix plus élevé, fini (+0,4 % à 20 ans), et un salaire réel plus élevé
  (+0,8 %) : c'est l'hystérèse de niveau propre à l'union monétaire diagnostiquée en A.2. Le choc énergétique est un choc
  de termes de l'échange : les salariés en supportent la perte (salaire réel −6,4 %), car la cible des salaires est en
  prix de VA.
- **Consommation, épargne, investissement.** Une hausse d'impôts des ménages réduit la consommation de 1,9 % à 20 ans.
  L'investissement répond au coût d'usage : +1,6 % pour une baisse d'IS de 5 points, −1,8 % pour une hausse de taux
  d'un point. Les dividendes et la dette des sociétés réagissent dans le sens attendu.
- **Production-emploi-chômage.** Multiplicateur de demande publique de 1,25 la 1re année, 0,78 à 5 ans et 0,20 à
  20 ans (fermeture). Un choc de productivité ne change pas l'emploi à long terme (−17 000 à 20 ans) : neutralité de long
  terme vérifiée. L'identité chômage-emploi tient dans tous les chocs.
- **Finances publiques.** L'allègement de coût du travail coûte 0,74 point de PIB la 1re année et 0,76 à 5 ans : le
  surcroît d'activité ne le finance pas, car la baisse des prix réduit les recettes nominales. Le coût net d'une baisse
  d'IS passe de 0,53 point la 1re année à 0,36 à 20 ans (investissement, transfert de bénéfices). Les effets sur la dette à 20 ans sont amplifiés par la
  référence, dont la dette est explosive (§ 7.1) : ils ne doivent pas être lus comme des ordres de grandeur robustes.
- **Extérieur.** Un choc de demande mondiale n'a plus d'effet sur le PIB après 20 ans, car l'offre est contrainte par la
  fermeture ; le solde extérieur s'améliore de 0,7 point. Le choc énergétique dégrade le solde extérieur de 5 points.

**v0.9 et P4** : réponses très proches. Les écarts portent sur le partage prix-marges des chocs de coût, plus durable en
marges en P4, et sur les canaux propres au compte des sociétés (dividendes, dette des SNF).

### 3.3 Décomposition par gel des boucles (P4)

Chaque boucle est figée sur la trajectoire de référence (`Exogenes.gel`), seule ou avec les autres ; écart du PIB (%)
et de l'emploi (milliers) à 1, 5 et 20 ans.

| Choc | Tout gelé | Seule active : consommation | Seule active : prix-salaires | Seule active : emploi | Seule active : fermeture | Complet |
|---|---|---|---|---|---|---|
| Demande publique, PIB | 0,97 / 0,98 / 1,04 | 1,18 / 1,18 / 1,19 | 0,99 / 0,90 / 0,34 | 0,97 / 0,98 / 1,04 | 0,97 / 0,69 / 0,16 | 1,25 / 0,78 / 0,20 |
| Coût du travail −2 %, emploi | 0 / 0 / 0 | 0 / +2 / +3 | +1 / +2 / +4 | 0 / +145 / +187 | 0 / 0 / 0 | +25 / +106 / +81 |
| Taux +1 pt, emploi | 0 / −1 / −1 | −3 / −3 / −2 | 0 / −1 / −1 | −2 / −17 / −42 | 0 / −1 / −10 | −11 / −33 / −112 |

- Le multiplicateur de court terme vient de la consommation (+0,2). L'éviction de long terme vient de la fermeture
  (1,04 → 0,16) et de la boucle prix-salaires (perte de compétitivité, prix +2,7 % à 20 ans).
- L'effet d'un allègement sur l'emploi passe par la substitution capital-travail (σ). Les boucles se combinent de façon
  non additive : l'effet complet (+106 000 à 5 ans) est inférieur à celui de la seule boucle d'emploi (+145 000), parce
  que la baisse des prix de VA réduit la baisse du coût réel du travail (c / p_va), donc la substitution.
- Le choc de taux agit d'abord par le capital (emploi), puis par la fermeture.

---

## 4. Estimation, calibration et justifications

Légende : [E] estimé ; [C] calibré sur l'année de base ou la littérature ; [H] hypothèse. Le registre complet des
paramètres antérieurs est dans `doc/20_registre_parametres_v08.md`.

| Paramètre | Valeur | Statut | Source, justification | Variantes |
|---|---|---|---|---|
| σ (capital-travail) | 0,45 | [C] | non identifié (3.4) ; milieu de la littérature | 0,3 ; 0,6 |
| Tendance d'efficience du travail | CPO CES en heures, 8 ans | [E] | phase 3.4 | |
| Fermeture ρ, θ | 0,2 ; 0,75 | [E] | inférence indirecte sur AMECO et FMI (3.1) | fermeture v0.6 |
| Prix de VA : cible | frontière θ_b CSU + (1 − θ_b) coût du capital | [E] dynamique ; [C] θ_b | A.2 ; θ_b = part du travail de la branche | v0.9 (CSU seul) |
| Effet du TUC sur les prix | 0 | [E] non significatif | 0,001 ± 0,001 | v0.9 |
| Pente des prix κ | 0,10 | [C] | non identifiée (A.2) | × 0,5 ; × 2 |
| Indexation des salaires (court terme) | 0,39 | [E] | équation annuelle v0.9 | rattrapage 0,17 (T2) |
| Phillips (salaires) | −0,004 | [C] | non identifiée en annuel et en trimestriel | × 0,5 ; × 2 |
| Taux apparent des SNF : vitesse, poids du court, transmission, écart | 0,60 ; 0,77 ; 1,29 ; 3,4 | [E] 1999-2024 | M21 | μ = 0,35 ; 0,83 |
| Intérêts reçus / versés | 0,77 (2019) | [C] | stable 2010-2025 | |
| Taux de distribution des dividendes | 0,36 du résultat t − 1 | [C] | Lintner non identifié | lissage 0,3 |
| Effets de la fiscalité des dividendes | 0 | [H] | signe instable | variante Lintner |
| Dette des SNF / besoin de financement | 1,06 | [E] (± 0,31) | 1997-2019 | 0,5 ; 1,5 |
| Élasticité de l'IS au taux légal (mesure) | 1 × transfert de bénéfices | [H] + [L] | élasticité historique −0,10 ± 0,29 (assiette) | taux apparent observé |
| Autofinancement → investissement | 0 | [E] non significatif | p = 0,26 à 0,59 | |
| Dette publique par cohortes | structure AFT | [C] | validée sur la règle AFT (3.4) | renouvellement 1/8 |

Principes appliqués :
- aucun paramètre n'est choisi pour améliorer une rétrosimulation particulière ;
- quand un paramètre n'est pas identifié, il est calibré, documenté, et ses variantes sont simulées (§ 5.5) ;
- les équations de taux d'intérêt sont estimées jusqu'en 2024, car 2022-2024 est le seul épisode de hausse des taux
  de l'échantillon ; les dividendes, la dette et l'IS sont estimés sur 1997-2019, comme les autres comportements.

---

## 5. Résultats des tests et simulations

### 5.1 Rétrosimulations conditionnelles (niveau 2)

Écart en dernière année, simulé − observé (`phase43/b3_backtests.log`) :

| Origine | Configuration | PIB (%) | Prix conso (%) | Emploi (%) | Chômage (pt) | Dette (pt PIB) |
|---|---|---|---|---|---|---|
| 2010 → 2019 | v0.9 | +1,38 | +0,83 | +1,13 | −1,04 | +1,81 |
| | P4 | +1,64 | +1,36 | +1,66 | −1,52 | −4,64 |
| 2014 → 2019 | v0.9 | −0,43 | −1,29 | +0,30 | −0,27 | −1,68 |
| | P4 | −0,42 | −1,53 | +0,27 | −0,25 | −1,77 |
| 2019 → 2024 | v0.9 | +1,12 | −3,89 | −1,60 | +1,49 | −3,80 |
| | P4 | +0,90 | −3,20 | −1,65 | +1,53 | −5,93 |

Erreurs quadratiques moyennes annuelles : équivalentes sur la croissance du PIB (écart de 0,05 point au plus) ; égales
ou meilleures pour P4 sur l'inflation (0,57 contre 0,58 en 2014-2019 ; 1,55 contre 1,65 en 2019-2024). P4 est moins bonne sur le niveau des prix et la dette depuis
l'origine 2010, déjà le cas de T1 (A.2).

### 5.2 Compte des sociétés

Voir `phase43/NOTE_B.md`. Compte isolé à moteurs observés : intérêts nets à −6 / +12 Md€, IS à ±3 %, épargne à ±10 %.
Dividendes à −37 / +32 %, à cause de la tendance du taux de distribution. Identités exactes.

### 5.3 Prévisions ex ante (niveau 3) et comparaison au FMI

Voir `phase43/NOTE_C.md`. Origines 2010-2016, erreur absolue moyenne :
- **croissance** : modèle ex ante 0,39 à 1 an et 0,25 à 5 ans, contre 0,59 et 0,34 pour le FMI du même millésime et
  0,84 et 0,38 pour la prévision naïve ;
- **inflation** : moins bonne que le FMI (0,72 contre 0,43 à 1 an) ;
- **dette** : biais de +10,6 points à 5 ans, dû à la convention de législation inchangée (4,5 points en conditionnel).

Origine 2021 : le PIB nominal conditionnel est sous-estimé de 7,6 % en 2024 (volume −3,9 %, déflateur −3,9 %), d'où
des recettes trop basses de 121 Md€ et 16 points de dette en trop. Le dénominateur explique 10 de ces 16 points. C'est
l'épisode 2022-2024, hors du cadre estimé.

### 5.4 Choc de politique identifié : le CICE (niveau 4)

Rétrosimulation 2012-2018, avec − sans CICE, coût budgétaire compté (`phase43/resultats/c2_choc_cice.json`) :

| | 2014 | 2016 | 2017 | Évaluations ex post |
|---|---|---|---|---|
| Emploi marchand, P4 (milliers) | +38 | +71 | +86 | ≈ 100 000 (micro, 2013-2016) ; ≈ 160 000 (macro-sectorielle, 2013-2017) ; France Stratégie 2020 |
| Emploi marchand, v0.9 | +37 | +64 | +76 | |
| Prix conso, P4 (%) | −1,2 | −1,4 | −1,6 | |
| Taux de marge, P4 (pt) | +0,5 | +0,4 | +0,5 | |
| Solde public, P4 (pt PIB) | −0,8 | −0,6 | −0,8 | |

Le modèle se situe en dessous des évaluations ex post : 71 000 emplois en 2016, contre environ 100 000 en
micro-économétrie. P4 s'en rapproche plus que la v0.9. L'écart est cohérent avec une transmission aux prix plus forte
que celle mesurée ex post, et avec un effet de substitution limité par σ = 0,45 ; avec σ = 0,6, l'effet d'emploi d'un
allègement est 5 % plus fort à 5 ans (§ 5.5).

### 5.5 Sensibilité aux paramètres non identifiés (P4)

Base : rétrosimulation 2010-2025, chocs en 2011 ; écarts à 5 / 15 ans (`phase43/resultats/e1_sensibilite.csv`).

| Variante | Demande publique +5 % : PIB | Demande : prix | Coût du travail −2 % : emploi (milliers) | Taux +1 pt : PIB |
|---|---|---|---|---|
| central | 0,98 / 0,51 | 1,07 / 4,03 | +71 / +41 | −0,91 / −2,37 |
| σ = 0,3 / 0,6 | 0,98 / 0,47 ; 0,97 / 0,54 | ≈ central | +56 / +24 ; +74 / +66 | −0,92 / −2,20 ; −0,90 / −2,40 |
| Phillips × 0,5 / × 2 | 0,93 / 0,34 ; 1,07 / 0,82 | 0,71 / 2,31 ; 1,78 / 7,53 | ≈ central | −0,91 / −2,16 ; −0,92 / −2,80 |
| Pente des prix κ × 0,5 / × 2 | ≈ central | 0,91 / 3,67 ; 1,37 / 4,75 | ≈ central | ≈ central |
| Rattrapage salarial 0,17 | 0,98 / 0,54 | 1,14 / 4,67 | +72 / +45 | −0,91 / −2,43 |
| Paramètres du compte des sociétés (μ, φ, lissage) | identiques à 0,01 près | identiques | identiques | identiques |
| Fermeture v0.6 (chômage) | 0,30 / 0,07 | 1,05 / 2,63 | +54 / −3 | −0,55 / −0,05 |

Constats :
1. **La fermeture est le paramètre le plus influent à moyen et long terme.** Elle divise par trois le multiplicateur à
   5 ans et annule l'effet d'emploi d'un allègement à 15 ans.
2. **La pente de Phillips gouverne la dérive des prix** après un choc de demande permanent (+2,3 % à +7,5 % à 15 ans).
3. **σ gouverne l'effet d'emploi des baisses de coût** (+24 000 à +66 000 à 15 ans).
4. Les paramètres du compte des sociétés n'affectent que ce compte et les dividendes, pas les agrégats.
5. **L'effet d'un choc de taux dépend du niveau des taux** : PIB −0,91 % à 5 ans sur la base 2010-2025 (taux proches de
   zéro), −0,15 % sur la référence 2027-2046 (OAT 4,9 %). Le coût d'usage est en log de (r + δ), donc un point de taux
   pèse beaucoup plus quand les taux sont bas.

---

## 6. Arbitrages et variantes écartées

| Phase | Variante | Raison de l'écart | Statut |
|---|---|---|---|
| 4.1 | Fermeture v0.6 (chômage) comme centrale | v0.8 estimée (3.1) ; convergence des fermetures en v0.9 | conservée en variante |
| 4.2 A | Prix de production « à la Mésange » | rejetée par les données (transmission des CI 0,96 ; erreurs de prix de VA amplifiées) | archivée |
| 4.2 A | Salaires ciblant le prix à la consommation (W4, W6) | inflation de conflit instable (+10 à +79 % de prix) | archivée, activable |
| 4.2 A | Prix de VA avec hausses des CI (V4) | pas de gain hors échantillon | activable |
| 4.2 A.2 | Effet du TUC sur les prix | non significatif, dérive explosive après un choc de taux | retiré dans T0, T1, T2 |
| 4.2 A.2 | Capacité au capital désiré | inverse la dérive (déflation) sans la régler | activable |
| 4.2 A.2 | Prix de VA trimestriels | instables, correction d'erreur de mauvais signe | non utilisés |
| 4.2 A.2 | Coût du capital estimé librement | poids nul ; frontière retenue pour sa cohérence avec la CES, à ajustement égal | |
| 4.2 A.2 | Transmission des baisses de coût selon la tension, l'exposition ou les marges | non identifiée | |
| 4.3 B | Équation de Lintner des dividendes | vitesse non significative ; moins bonne hors échantillon | archivée (rapport d'estimation) |
| 4.3 B | Solde des dividendes de S11 comme variable de comportement | différence de deux flux bruts, trop volatile | |
| 4.3 B | Taux apparent sur le seul taux à 10 ans | R² 0,51 ; erreurs de −1 à −1,9 pt | |
| 4.3 B | Vitesse estimée sur 1999-2019 (0,83) | +2,1 pt d'erreur en 2023-2024 | variante haute |
| 4.3 B | Équation de taux des intérêts reçus | R² 0,48, transmission 2,8 | remplacée par un rapport |
| 4.3 B | Actifs liquides indexés sur le PIB | intérêts reçus sous-estimés de 11 à 40 Md€ | |
| 4.3 B | IS proportionnel au taux légal en rétrosimulation | contredit par les données (élasticité −0,10 ± 0,29) | taux apparent observé injecté |
| 4.3 B | Canal autofinancement → investissement | non significatif | non ajouté |
| 4.3 C | Fiscalité de B dans les prévisions ex ante remplacée par les mesures annoncées | information non disponible de façon homogène et ouverte | convention de législation inchangée, documentée |

Arbitrages qui restent ouverts (choix de scénario, pas d'estimation) :
- réaction de la politique monétaire à l'inflation de la zone euro (ancrage plus fort) ;
- règle budgétaire dans la référence de long terme (§ 7.1).

---

## 7. Limites et paramètres incertains

### 7.1 Limites structurelles

1. **Dette publique explosive dans la référence de long terme.** OAT maintenue à 4,89 % (dernier niveau mensuel
   observé, octobre 2026) et déficit primaire croissant (vieillissement, consommation publique au rythme 2011-2019) :
   le déficit passe de 5 % du PIB en 2025 à 22 % en 2047, et la dette atteint 300 % du PIB. La v0.9 et P4 sont
   identiques sur ce point. Aucune règle de réaction budgétaire ni de prime de risque n'existe. Les effets des chocs sur
   la dette à 15-20 ans sont donc amplifiés par l'effet boule de neige.
2. **Ancrage nominal.** Pas de politique monétaire endogène, canal de compétitivité faible. Un choc de demande permanent
   déplace durablement les prix (+2 % à 20 ans, +2,3 % à +7,5 % selon la pente de Phillips). Un choc salarial
   temporaire laisse un salaire réel plus élevé de 0,8 %.
3. **Épisode 2022-2024 hors du cadre estimé** : inflation, salaires et profits sous-estimés (rétrosimulation
   conditionnelle 2021 : PIB nominal −7,6 % en 2024).
4. **Profits et taux de distribution.** La tendance du taux de distribution n'est pas modélisée, ni la hausse des marges
   industrielles de 2022-2023.
5. **Effets non linéaires des taux** : coût d'usage en log de (r + δ).
6. **Comptes non modélisés** : S12 sans comportement ; intérêts et D44 des ménages indexés sur le PIB ; pas de bilan
   des ménages.
7. **Multiplicateur de demande publique de 1,25 la première année**, dans le haut des estimations pour la France. Il
   dépend de la fermeture, qui le divise par trois en variante v0.6.
8. **Pas annuel** : le système trimestriel (M20) n'est estimé que pour les salaires.

### 7.2 Paramètres restant incertains (ordre d'influence)

1. La fermeture (ρ, θ, et le choix production ou chômage) : multiplicateurs, effets de long terme.
2. La pente de Phillips (salaires) et la pente des prix κ : ancrage nominal.
3. σ : effet d'emploi des mesures de coût du travail.
4. Le partage prix-marges des baisses de coût : frontière (T1) ou CSU seul (v0.9).
5. Le taux de distribution des dividendes et sa sensibilité à la fiscalité.
6. Le renouvellement de la dette des SNF (μ de 0,35 à 0,83).

---

## 8. Tableau des tests

| Domaine | Test | Résultat |
|---|---|---|
| Non-régression | v0.9 reproduite après les phases 4.2 et 4.3 (origine 2014, 5 agrégats, 1e-6) | réussi |
| Non-régression | v0.8 reproduite (origine 2014) | réussi |
| Non-régression | v0.8 reproduite après un essai v0.9 (défaut de fuite d'état corrigé en 4.3) | réussi après correction |
| Non-régression | suites v0.8 `test_phase31.py` et `test_phase3.py` (26 tests, référence 2047, 1 h 17) | 24 réussis, 2 échecs antérieurs à la phase 4.3 (ci-dessous) |
| Configuration | `configurer_v08` rétablit σ ; `configurer_phase4` garde σ = 0,45 | réussi |
| Unitaire | Règle légale du SMIC reproduite 2013-2021 (écart < 1,3 pt) | réussi |
| Unitaire | Indice de prix des CI = 1 à l'année de base | réussi |
| Unitaire | Identités B8G et B9 de S11 dans les données (1995-2025) | réussi (écart 0) |
| Unitaire | Compte des sociétés isolé : continuité à la base et identités | réussi |
| Unitaire | Hausse des taux → intérêts en hausse, dividendes en baisse, dette en hausse | réussi (1er essai échoué : seuil du test mal posé sur les intérêts nets, corrigé pour porter sur les intérêts versés) |
| Unitaire | Millésimes FMI disponibles, exogènes ex ante sans information future | réussi |
| Intégration | P4 : identités du compte des sociétés et reconstruction exacte des revenus du capital des ménages | réussi |
| Intégration | P4 ne dégrade pas la rétrosimulation 2014-2019 de T1 (< 0,3 pt ; dette < 1 pt) | réussi |
| Ancrage | T1 : choc salarial temporaire, inflation revenue sous 0,1 pt dès la 5e année ; prix stabilisés | réussi |
| Stabilité | T1 et P4 : pas d'emballement après un choc de taux (15 ans) ; intérêts SNF en hausse, dividendes en baisse | réussi |
| Intégration | 10 chocs × 2 configurations sur 20 ans : 142 contrôles automatiques (signes, stabilité, identités, chômage-emploi) | 142 sur 142 réussis (1er essai : 4 échecs dus à une formule de contrôle erronée, corrigée) |
| Identités | Dette publique (variante − référence), à 1e-9 près (4.1) | réussi |
| Identités | Compte des sociétés dans toutes les simulations (< 1e-9 M€) | réussi |
| Validation | Rétrosimulations conditionnelles, 5 origines × 3 configurations | voir § 5.1 et 5.3 |
| Validation | Prévisions ex ante comparées au FMI et à une prévision naïve | croissance : meilleure que le FMI ; inflation et dette : moins bonne |
| Validation | Choc CICE comparé aux évaluations ex post | en dessous (71 000 contre ≈ 100 000 en 2016) |
| Sensibilité | 13 variantes × 3 chocs | § 5.5 |

Échecs des suites v0.8, antérieurs à la phase 4.3 et non corrigés (ils portent sur la v0.8, à laisser intacte) :
- `test_offre_travail_heterogene` : le test de la phase 3 attend des clés `rsa|seul`, alors que M15 distingue depuis la
  v0.8 (commit 51927cb) locataires et propriétaires (`rsa|seul|locataire`). C'est un test périmé, M15 n'a pas été
  modifié en phase 4.
- `test_choc_de_productivite_defavorable` : à 20 ans, la dette baisse de 7,9 points au lieu d'augmenter. Les autres
  assertions du test (PIB, potentiel, écart de production) passent. Le code par défaut de la v0.8 n'a pas changé
  (reproduction exacte des rétrosimulations) ; l'explication la plus probable, non vérifiée, est la référence 2047
  recalculée avec les données d'octobre 2026 (OAT 4,89 %, dette explosive, où la hausse des prix d'un choc de
  productivité défavorable réduit le ratio de dette). C'est la même limite qu'au § 7.1.

Échecs rencontrés pendant la phase 4.3, tous corrigés et conservés dans l'historique :
- une ligne de `configurer_v08` (rétablissement de σ) avait été déplacée par erreur dans `configurer_phase4` lors de
  l'ajout de cette fonction. La référence P4 avait donc été calculée avec σ = 0,40. Défaut détecté par le test de
  non-régression v0.8, corrigé, référence et chocs recalculés, test ajouté ;
- le contrôle chômage-emploi de la batterie de chocs avait une formule fausse (facteur 1 − u), corrigée ;
- l'import de la fonction de chocs de la phase 4.2 relançait toute sa batterie : garde `__main__` ajoutée.

---

## 9. Bilan de maturité

| Composante | Niveau | Commentaire |
|---|---|---|
| Cadre comptable, Leontief, identités | **validé** | identités exactes dans toutes les simulations |
| Emploi CES, potentiel, non marchand | **validé** | erreurs d'emploi compensées supprimées (3.4) ; σ calibré |
| Dette publique par cohortes | **validé** | règle AFT reproduite, taux apparent RMSE 0,15 |
| Compte des sociétés (intérêts, IS, épargne, dette) | **validé** | comportements estimés ou calibrés, identités exactes, tests hors échantillon |
| Dividendes | **fragile** | règle proportionnelle ; tendance et fiscalité non identifiées |
| Prix de VA (frontière) | **validé avec réserve** | ajustement égal à la v0.9, meilleur ancrage, choix théorique |
| Salaires et ancrage nominal | **fragile** | Phillips non identifiée ; hystérèse de niveau ; 2022-2024 non expliqué |
| Demande (consommation, investissement, commerce) | **validé** | prévision de croissance meilleure que le FMI à 1 et 5 ans |
| Fermeture et multiplicateurs | **fragile** | paramètre le plus influent ; multiplicateur 1,25 |
| Finances publiques à long terme | **à traiter** | référence explosive ; pas de règle budgétaire |
| Effets des taux | **fragile** | non-linéarité du coût d'usage ; dépend du niveau des taux |
| Politique de coût du travail | **validé avec réserve** | sous l'évaluation ex post du CICE |
| Validation prédictive | **validé** | protocole à 4 niveaux implémenté et reproductible |
| Pas trimestriel | **à traiter (phase 5)** | seuls les salaires sont estimés en trimestriel |

---

## 10. Recommandation sur la phase 5

**Le modèle peut passer en phase 5, à trois conditions préalables, et avec P4 comme configuration de travail.**

Arguments :
- toutes les interactions prévues sont implémentées et vérifiées sur 20 ans (142 contrôles sur 142), sans dérive ni
  explosion des écarts ;
- les identités comptables sont exactes ;
- les tests de non-régression passent ;
- les performances prédictives sont du niveau des prévisions institutionnelles sur la croissance.

**Remplacement de la v0.9 par P4 comme référence : pas encore.** P4 est meilleure sur l'ancrage et les mécanismes, mais
pas sur l'ajustement (moins bonne sur le niveau des prix depuis 2010). La v0.9 reste la référence reproductible. P4
devient la configuration de travail de la phase 5, et la décision formelle sera prise après les conditions 1 et 2.

Conditions préalables (en début de phase 5) :
1. **Référence de long terme soutenable**, sans quoi les résultats à 15-20 ans sur la dette ne sont pas
   interprétables. Il faut choisir :
   - une règle de réaction budgétaire (solde primaire réagissant à la dette), ou
   - une convention de référence stabilisante,
   - et, le cas échéant, une prime de risque sur l'OAT.
2. **Choix de l'ancrage nominal** : politique monétaire exogène (actuelle) ou règle de réaction de la BCE à l'inflation
   de la zone euro, en scénario. Les variantes de la pente de Phillips doivent être publiées avec tout résultat de long
   terme.
3. **Passage au pas trimestriel** sans réestimer d'abord tout le modèle. Interpolation des exogènes et des équations
   annuelles, en conservant les cibles de long terme. Les équations trimestrielles (salaires M20) servent de test de
   cohérence. Le calendrier des dividendes (exercice t − 1) et de la dette (fin de période) est déjà compatible.

À traiter pendant la phase 5, sans bloquer :
- la tendance du taux de distribution ;
- les intérêts des ménages ;
- les marges de 2022-2023 ;
- le multiplicateur et la fermeture (publier les variantes v0.6) ;
- la non-linéarité de l'effet des taux.
