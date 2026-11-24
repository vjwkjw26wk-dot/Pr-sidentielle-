# 22 — Phase 5 : note méthodologique (références budgétaires, pas trimestriel, régimes de politique économique)

Base de travail : configuration P4 (`configurer_phase4()`), v0.9 conservée comme référence reproductible. Cette note
fixe les arbitrages avant implémentation ; elle ne modifie pas le code.

## 0. Principe d'organisation : séparer environnement, régime et programme

Toute simulation est le produit de trois couches indépendantes :

| Couche | Contenu | Qui la fixe |
|---|---|---|
| **Environnement** E | démographie, économie mondiale, prix de l'énergie, recalage 2023-2025, FMI 2026-2031 | données et conventions communes |
| **Régime de politique économique** R | règle budgétaire, réaction monétaire, prime de risque, jeu de paramètres fragiles | hypothèse explicite, choisie par l'utilisateur |
| **Programme** P | mesures (prélèvements, dépenses, réglementation) | objet de l'évaluation |

**Effet d'un programme** : Δ(P | E, R) = Y(E, R, P) − Y(E, R, ∅). Il est toujours calculé à environnement et régime
identiques. On publie une matrice programmes × régimes, jamais un effet de programme mélangé à un changement de régime.

Toute sortie distingue deux catégories :
- **imposé** : effort budgétaire ex ante, trajectoire de taux si exogène, paramètres ;
- **produit** : solde, dette, PIB, prix, emploi.

## 1. Trajectoires de référence budgétairement cohérentes

### 1.1 Diagnostic de la référence actuelle (P4, 2025 → 2047)

| Poste (% du PIB) | 2025 | 2047 | Variation | Nature |
|---|---|---|---|---|
| Dépenses hors intérêts | 55,0 | 62,2 | +7,2 | |
| dont prestations | 18,7 | 21,5 | +2,9 | pensions M9 (législation) + autres prestations en volume +1,37 %/an |
| dont autres dépenses | 36,4 | 40,7 | +4,3 | **convention** : consommation publique en volume +1,34 %/an (rythme 2011-2019) |
| Recettes | 52,2 | 54,3 | +2,0 | modèle (assiettes) |
| Intérêts | 2,3 | 13,8 | +11,5 | **effet boule de neige** : taux apparent 4,9 % (OAT à 4,89 % maintenue), croissance nominale de 2,5 à 1,8 % |

Le cœur du problème vient des conventions de la référence, pas d'un mécanisme du modèle. La consommation publique
croît en volume à son rythme passé (+1,34 %/an) alors que le PIB ralentit (+0,8 % en 2035, +0,4 % en 2047, du fait de
la population active). Sa part dans le PIB augmente donc mécaniquement. L'emploi non marchand passe de 9,35 à 11,1
millions. Le tout est amplifié par r > g.

**Choix recommandé : redéfinir « politique inchangée ».** La consommation publique et les prestations hors pensions
suivent la croissance potentielle en volume, c'est-à-dire une part constante du PIB potentiel.
- C'est la convention habituelle des projections à législation inchangée : constance des volumes par habitant ou de la
  part dans la richesse, pas prolongement d'une tendance de dépense.
- L'ancienne convention reste disponible comme variante R0-h (« rythme historique ») et doit être présentée comme une
  hypothèse de dépense, pas comme une politique inchangée.
- Les pensions restent régies par la législation (M9).
- La consommation publique est un exogène de la référence, pas un comportement : changer sa convention ne rouvre pas
  la phase 4.

### 1.2 Familles de références

| Code | Définition | Budgétaire imposé | Produit par le modèle |
|---|---|---|---|
| **R0** | politique inchangée (convention de 1.1) | rien au-delà de la loi de finances 2026 | solde, dette (même divergente) |
| R0-h | variante : consommation publique au rythme historique | id. | id. |
| **R1** | stabilisation du ratio de dette au niveau atteint en T₀ (2027 par défaut) | effort ex ante selon la règle (1.3), plafonné | solde, dette, effets sur l'activité |
| **R2** | ajustement progressif vers une cible (dette d*, ou solde primaire structurel s*) | effort ex ante selon la règle, plafonné, clause d'écart | id. |

R1 et R2 ne garantissent pas la soutenabilité. Si l'effort plafonné ne suffit pas, la dette continue d'augmenter et le
modèle le montre : la règle est imposée, la soutenabilité est un résultat.

### 1.3 Règle de réaction budgétaire (une seule forme, paramétrée)

Variables, en points de PIB nominal :
- d : ratio de dette ;
- s : solde primaire ajusté du cycle, s = solde primaire − ε × écart de production. ε ≈ 0,5 est l'ordre de grandeur des
  semi-élasticités budgétaires européennes ; il sera à mesurer sur le modèle (test du § 5) ;
- e_t : effort ex ante cumulé.

**Solde primaire stabilisant** (calculé en temps réel, sans information future) :

    s̄_t = (r̄_t − ḡ_t) / (1 + ḡ_t) · d_{t−1}

avec r̄ le taux apparent et ḡ la croissance nominale potentielle, en moyennes mobiles sur 3 ans.

**Cible :**
- R1 : s*_t = s̄_t ;
- R2 : s*_t = s̄_t + β (d_{t−1} − d*), avec par exemple β = 0,02 : 2 % de l'écart à la cible résorbé chaque année
  par le solde.

**Effort :**

    Δe_t = clip( α (s*_t − s_{t−1}) , 0 , Δe_max )   si écart de production > −g_esc
    Δe_t = 0                                          sinon (clause d'écart)

Paramètres :
- α = 0,5 : demi-convergence annuelle ;
- Δe_max = 0,5 point par an, ordre de grandeur des règles européennes ;
- g_esc = 1,5 point d'écart de production négatif.

L'effort ne devient pas négatif en central (pas de relâchement automatique) ; une variante symétrique est possible.

**Instruments.** L'effort ex ante est réparti selon des parts paramétrables w_k (Σ w_k = 1) entre les leviers déjà
présents dans M8 :
- consommation publique en volume (`conso_publique`) ;
- prestations (`ajust_prestations`) ;
- impôts des ménages (`niveaux["impots_menages_pib"]`) ;
- impôts sur les produits (`niveaux["impots_produits"]`).

Défaut : moitié dépenses (conso publique 30 %, prestations 20 %), moitié recettes (impôts des ménages 30 %, impôts sur
les produits 20 %). C'est une hypothèse affichée, pas une calibration. La variante « redressement » de M8_reference
suit déjà ce principe.

**Conséquences économiques attendues** :
- l'effort ex post est inférieur à l'effort ex ante (multiplicateurs de la 1re année, § 3.2 du rapport 21 :
  de 0,5 pour les impôts sur les produits à 1,25 pour la consommation publique) ;
- la stabilisation coûte de l'activité à court terme ;
- avec la fermeture v0.8, l'effet sur le PIB s'efface en grande partie à long terme, alors qu'avec la fermeture v0.6 il
  persiste plus longtemps ;
- la clause d'écart évite les spirales procycliques.

### 1.4 Règle figée ou active dans l'évaluation des programmes

C'est le point qui évite de confondre l'effet d'un programme avec celui de la politique budgétaire.

- **Figée (défaut)** : la référence R1 ou R2 est simulée avec la règle active ; la trajectoire d'effort e_t obtenue est
  ensuite imposée telle quelle dans la simulation avec programme. L'effet mesuré est celui du programme non compensé :
  son coût apparaît dans le solde et la dette.
- **Active (variante)** : la règle reste active avec le programme. Le programme est alors « financé » par la règle, et
  l'effet mesuré inclut le financement (impôts ou économies induits).
- La différence entre les deux est publiée comme **effet de la réaction budgétaire au programme**.

### 1.5 Prime de risque souveraine (option, désactivée par défaut)

    OAT_t = OAT^exo_t + γ · max(0, d_{t−1} − d_s)

avec par exemple γ = 0,03 point par point de dette et d_s = 90 %. Les valeurs sont à documenter à partir de la
littérature et du diagnostic de prime de risque de la phase 3.1 ; elles ne sont pas estimées ici.

C'est une hypothèse de régime, pas une partie de l'environnement. Activée avec R0, elle peut rendre la trajectoire
explosive plus vite. C'est un résultat à montrer, pas à corriger.

## 2. Passage au pas trimestriel

### 2.1 Méthodes comparées

| Méthode | Principe | Réalisme | Robustesse | Complexité | Fausse précision |
|---|---|---|---|---|---|
| A. Réestimation trimestrielle complète | toutes les équations estimées sur données trimestrielles | élevé si les données existent | faible : pas de panel de 25 branches ni de comptes de secteurs trimestriels publics ; Phillips et prix de VA non identifiés en trimestriel (A.2) | très élevée | non |
| **B. Conversion de fréquence des équations annuelles** | mêmes cibles de long terme ; vitesses et impacts convertis ; dynamique calée pour que le modèle trimestriel agrégé reproduise les réponses annuelles | moyen à bon | élevée : ancré sur l'annuel validé | moyenne | faible, si la sortie de référence reste annuelle |
| C. Modèle annuel + interpolation des sorties (Denton, Chow-Lin) | résolution annuelle, profil infra-annuel interpolé | nul : aucune dynamique infra-annuelle | élevée | faible | **forte** : le profil trimestriel ne vient d'aucun mécanisme |
| D. Fréquences mixtes | blocs rapides trimestriels, blocs lents annuels | bon | moyenne : interfaces délicates | élevée | moyenne |

**Recommandation : méthode B**, avec le modèle annuel P4 conservé comme jumeau de contrôle. Le trimestriel ne doit
rien changer à moyen terme ; il ajoute :
- le calendrier des mesures (entrée en vigueur en cours d'année) ;
- les délais de transmission des chocs rapides (énergie, taux, salaires) ;
- un pas compatible avec des règles de réaction réalistes.

Les résultats publiés restent annuels par défaut. Les profils trimestriels sont des sorties de diagnostic.

### 2.2 Règles de conversion

**Équations à correction d'erreur.** L'équation annuelle

    Δx = a + b Δz + λ (x − x*)₋₁

devient, au pas trimestriel :

    Δx_q = a_q + b_q Δz_q + λ_q (x − x*)_{q−1}

1. La cible de long terme x* et les élasticités de long terme sont inchangées.
2. Vitesse de rappel : λ_q = 1 − (1 − λ_a)^{1/4}, ce qui préserve la demi-vie.
3. Impact b_q : déterminé pour que la réponse cumulée sur 4 trimestriels à un choc permanent de z égale la réponse
   annuelle de la 1re année. Il n'y a pas de formule fermée exacte (le rappel joue dans l'année) ; b_q se résout
   numériquement par équation, avec tolérance 1 %.
4. Constantes et tendances : a_q = a_a / 4.
5. Termes de calage de la référence : répartis également sur les 4 trimestres, en croissance.

**Retards.**
- Un retard annuel t − 1 devient un retard de 4 trimestres, ou une moyenne des trimestres t − 4 à t − 1 quand
  l'équation annuelle portait sur des moyennes annuelles (prix, salaires) ; le choix est fait équation par équation et
  documenté.
- Deux exceptions où l'information trimestrielle est déjà estimée :
  - salaires : M20 donne l'indexation dans le trimestre (0,28) et le rattrapage. Ils servent à fixer le profil
    intra-annuel, sous contrainte de l'équivalent annuel 0,39 + 0,17 ;
  - prix d'importation : transmission partielle θ, convertie comme une vitesse.

**Flux et stocks.**
- Flux au rythme trimestriel (non annualisés). Somme sur 4 trimestres = flux annuel, exact par construction.
- Stocks en fin de trimestre :
  - capital : K_q = (1 − δ_q) K_{q−1} + I_q, avec δ_q = 1 − (1 − δ)^{1/4} ;
  - dette publique : émissions et charges d'intérêts trimestrielles, cohortes M17 inchangées (maturités en années,
    coupons courus au trimestre) ;
  - dette des SNF : même principe.
- Ratios publiés comme les comptes nationaux : dette de fin d'année rapportée au PIB de l'année.

**Calendrier des flux annuels par nature.**
- **Dividendes** : versés aux 2e et 3e trimestres sur le résultat de l'exercice précédent (répartition à documenter
  par les comptes trimestriels de secteurs, sinon 50/50).
- **Impôts** :
  - IR prélevé à la source (contemporain depuis 2019) ;
  - IS en acomptes trimestriels sur le résultat précédent.
- **Prestations** : revalorisations aux dates légales, pensions au 1er janvier.
- **SMIC** : règle légale au 1er janvier, plus déclenchement automatique en cours d'année si l'inflation dépasse 2 %.

**Données disponibles seulement annuellement** (démographie, pensions M9, microsimulation M10, comptes de secteurs,
tableau entrées-sorties, panel de branches, exogènes FMI annuels) :
- exogènes en niveau lisse (population, volumes publics) : interpolation géométrique à croissance constante dans
  l'année, conservant la moyenne annuelle. Aucune saisonnalité, aucun profil inventé ;
- flux de mesures : montant annuel réparti selon le calendrier légal s'il existe, sinon également ;
- coefficients techniques (Leontief) : annuels, constants dans l'année ;
- **interdit** : interpoler des sorties endogènes ou importer un profil trimestriel non observé ;
- les séries réellement trimestrielles (taux, chômage, prix de l'énergie, demande mondiale) sont utilisées au
  trimestre pour le recalage.

**Identités.** Toutes les identités sont écrites au trimestre ; les agrégats annuels sont des sommes (flux) ou des
valeurs de fin de période (stocks). Il n'y a pas de recalage annuel a posteriori, qui masquerait une incohérence.

### 2.3 Critère d'acceptation (« jumeau annuel »)

Le moteur trimestriel est accepté si, agrégé annuellement :
1. la référence R0 diffère de la référence annuelle de moins de 0,1 % de PIB, 0,1 % de prix et 0,5 point de dette
   à tout horizon ;
2. les 10 chocs du rapport 21 (§ 3.2) donnent les mêmes réponses à 0,1 point près sur PIB, prix et solde à 5, 10 et
   20 ans, et à 0,2 point la 1re année (seule zone où le trimestriel peut légitimement différer) ;
3. les rétrosimulations 2014-2019 et 2010-2019 ne sont pas dégradées ;
4. les identités sont exactes au trimestre ;
5. le modèle est stable sur 80 trimestres.

## 3. Régimes de politique économique

### 3.1 Politique monétaire

| Code | Définition | Paramètres | Statut |
|---|---|---|---|
| **M0** | taux exogènes (court et long), trajectoire de l'environnement | — | central pour l'évaluation des programmes |
| **M1** | règle de la BCE (déjà estimée dans M11, 1999-2019, Euribor 3 mois) : i_t = a + 0,73 i_{t−1} + 0,39 π^ZE_t + 0,30 écart^ZE_t, réponse de long terme à l'inflation 1,44 | estimés [E] | variante |
| M1-c | M1 avec choc commun à la zone euro (énergie, demande mondiale) : la BCE réagit à l'inflation de toute la zone | idem | scénarios d'environnement |

Points de méthode :
- l'inflation et l'écart de la zone euro sont formés à partir des grandeurs françaises pondérées par environ 20 % (part
  de la France) et du reste de la zone, exogène ou M11 ;
- un programme français isolé ne déplace donc le taux de la BCE que d'environ 0,2 × 1,44 de son effet d'inflation,
  ce que M11 a déjà mesuré (« la BCE réagit peu ») ;
- M1 ne règle pas l'ancrage des prix français relatif à la zone (hystérèse de niveau, A.2) : la réaction de la BCE
  ancre l'inflation de la zone, pas le niveau des prix français. C'est un résultat économique à dire, pas un défaut à
  corriger ;
- taux long : taux court anticipé sur 10 ans (moyenne de la trajectoire de la règle) + prime de terme constante
  + prime souveraine (1.5) le cas échéant.

Au pas trimestriel, la règle est convertie en lissage trimestriel (ρ_q = 0,73^{1/4} ≈ 0,92, réponses de long terme
inchangées).

### 3.2 Politique budgétaire

- **B0** : pas de réaction (R0) ;
- **B1** : stabilisation (R1) ;
- **B2** : ajustement progressif (R2).

Chacune peut être figée ou active dans l'évaluation (1.4).

### 3.3 Paramètres fragiles : jeux nommés

Je ne recommande pas un plan factoriel complet (trop de combinaisons, lecture impossible). On utilise un jeu central
et deux jeux cohérents, plus les variations un à un déjà disponibles (`e1_sensibilite.py`).

| Jeu | Phillips (salaires) | Pente des prix κ | σ | Fermeture | Partage prix-marges |
|---|---|---|---|---|---|
| central | −0,004 | 0,10 | 0,45 | v0.8 (ρ 0,2, θ 0,75) | frontière (T1) |
| « ancrage faible, offre rigide » | × 2 | × 2 | 0,3 | v0.6 (chômage) | CSU seul (v0.9) |
| « ancrage fort, offre flexible » | × 0,5 | × 0,5 | 0,6 | v0.8 | frontière |

Chaque jeu est un objet de régime (couche R), appliqué à la référence et au programme.

### 3.4 Protocole de comparaison des programmes

1. **Résultat principal** : régime (B2 figé, M0, jeu central) — référence soutenable, programme non compensé, taux
   exogènes.
2. **Tableau de robustesse**, pour chaque programme, effets à 5 et 15 ans sous :
   - B0 et B1 ;
   - B2 actif ;
   - M1 ;
   - les deux jeux de paramètres extrêmes.
3. **Décomposition publiée** : effet propre (régimes figés) ; effet de la réaction budgétaire (actif − figé) ; effet de
   la réaction monétaire (M1 − M0).
4. **Classement des programmes** : il est dit robuste s'il est identique dans tous les régimes du tableau. Sinon,
   indiquer de quel régime il dépend.

## 4. Conséquences sur l'architecture actuelle

| Élément | Changement | Ampleur |
|---|---|---|
| `Exogenes` | séparer un objet `Regime` (règle budgétaire, monétaire, prime, jeu de paramètres) ; `Exogenes` = environnement + programme | moyen |
| `m8_reference` | calibrer une seule fois l'environnement (R0, ≈ 50 min, cache) ; R1, R2 et les jeux de paramètres = simulations du même environnement avec un régime, sans recalibration (≈ 10 s en annuel) | moyen ; **prérequis** |
| Convention de dépense de R0 | consommation publique et prestations hors pensions à part constante du PIB potentiel ; ancienne convention en variante | faible |
| Règle budgétaire | nouveau module M23 : calcul de e_t en fin d'année (variables retardées : pas de nouvelle boucle de point fixe), injection par les leviers existants | faible à moyen |
| Règle monétaire | réutiliser l'équation BCE de M11 dans la boucle annuelle (retardée d'une période en annuel, contemporaine au trimestre) au lieu de la boucle externe de M11 | moyen |
| Prime souveraine | option dans la fonction de taux (M17) | faible |
| Moteur trimestriel | nouveau moteur M8Q réutilisant les paramètres de M8 via une couche de conversion (2.2) ; M8 annuel conservé comme jumeau | **important** |
| Sorties | colonnes « imposé » (effort par instrument, taux si exogène) et « produit » ; annuel par défaut | faible |

### Prérequis réellement bloquants

1. **Temps de calibration de la référence** : 50 min par configuration. Sans la séparation environnement-régime,
   comparer 3 références × 3 jeux de paramètres × 2 régimes monétaires coûterait des heures et rendrait le moteur
   trimestriel inutilisable. À traiter en premier.
2. **Définition de « politique inchangée »** (1.1). C'est une décision, pas un développement, mais tout le reste en
   dépend : sans elle, R1 et R2 corrigeraient surtout une convention de dépense.

Aucun défaut de la phase 4 n'est bloquant. Les deux échecs des suites v0.8 portent sur la v0.8 (test périmé, signe
d'un effet sur la dette dans une référence explosive) et n'affectent pas P4.

## 5. Tests indispensables avant validation

**Règles budgétaires**
- B1 avec r et g constants : le ratio de dette converge vers son niveau de T₀ (±0,5 point) quand l'effort n'est pas
  plafonné ;
- B2 : convergence vers d*, monotone, à la vitesse impliquée par α et β ;
- plafond et clause d'écart respectés à chaque année ;
- aucun effort quand d < d* (R2) ;
- identité effort ex ante = Σ_k w_k × mesures injectées ;
- programme nul : effet nul dans tous les régimes ;
- règle figée = règle active pour un programme sans coût budgétaire.

**Politique monétaire**
- M1 avec part de la France nulle et zone euro à l'équilibre : identique à M0 ;
- état stationnaire i = r* + π* ;
- stabilité sur 20 ans pour les 10 chocs du rapport 21 ;
- un programme français isolé déplace le taux d'au plus 0,2 × 1,44 × son effet d'inflation.

**Pas trimestriel**
- identités trimestrielles exactes ; sommes annuelles exactes ;
- jumeau annuel (critères 2.3) ;
- interpolation des exogènes annuels : moyennes annuelles conservées exactement ;
- pas de profil trimestriel dans une sortie qui n'a pas de mécanisme infra-annuel (test : choc annuel constant →
  réponse trimestrielle monotone).

**Non-régression**
- tous les régimes désactivés et pas annuel : P4 reproduit à 1e-6 ;
- v0.9 et v0.8 reproduites (suites existantes).

**Protocole**
- additivité approximative des décompositions (effet propre + réaction budgétaire + réaction monétaire ≈ total,
  écart publié).

## 6. Plan d'implémentation priorisé

| Lot | Contenu | Dépend de | Livrable de contrôle |
|---|---|---|---|
| **5.0** | Objet `Regime` ; calibration de l'environnement une fois, régimes sans recalibration ; convention de dépense R0 (+ variante R0-h) | — | R0 en ≈ 10 s depuis le cache ; P4 inchangée |
| **5.1** | Module M23 : règle budgétaire (B1, B2), instruments, plafond, clause d'écart, modes figé et actif, sorties imposé / produit | 5.0 | tests de convergence ; références R0, R1, R2 comparées |
| **5.2** | Règle BCE (M11) intégrée à la boucle ; prime souveraine optionnelle | 5.0 | tests M1 = M0 dans les cas limites ; chocs d'intégration sous M1 |
| **5.3** | Jeux de paramètres nommés ; protocole programmes × régimes ; tableau de robustesse automatique | 5.1, 5.2 | matrice sur 2 programmes tests |
| **5.4** | Couche de conversion de fréquence ; moteur M8Q ; calendrier des flux | 5.0 | jumeau annuel (2.3) |
| **5.5** | Recalage trimestriel de l'environnement sur les séries trimestrielles disponibles | 5.4 | référence trimestrielle |
| **5.6** | Réévaluation des scénarios S1-S5 (chantier D) avec le protocole, en annuel puis en trimestriel | 5.3 (5.4 pour le trimestriel) | tableau de robustesse des programmes |

Ordre recommandé : 5.0 → 5.1 → 5.2 → 5.3, ce qui rend la comparaison des programmes possible en annuel, puis 5.4 et
5.5 en parallèle de 5.6. Le trimestriel n'est pas un prérequis pour comparer les programmes ; il précise les
dynamiques de court terme et le calendrier des mesures.

## 7. Décisions qui vous reviennent

1. La convention de « politique inchangée » (1.1).
2. Les cibles et paramètres de la règle R2 : d* ou s*, α, β, plafond, répartition entre instruments. Les valeurs
   ci-dessus sont des propositions, à afficher comme hypothèses.
3. Le régime du résultat principal (3.4). Proposition : B2 figé, M0, jeu central.
