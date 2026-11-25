# Données, estimations, calibrations et validation {#sec:donnees}

Un modèle macroéconométrique vaut ce que valent ses données et la façon dont ses paramètres ont été obtenus. Ce
chapitre présente les sources, la manière dont chaque paramètre a été fixé (estimation, calibration, littérature,
hypothèse), les méthodes d'estimation, les tests réalisés et, surtout, ce que ces tests prouvent et ne prouvent pas.

## Sources statistiques {#sec:sources}

**Principe : données ouvertes uniquement.** Toutes les données utilisées sont publiques, accessibles sans habilitation,
téléchargées par script et identifiées par une empreinte numérique (SHA-256) consignée dans un registre. Ce choix
garantit la reproductibilité mais exclut les données administratives individuelles (déclarations fiscales
individuelles, échantillons interrégimes de retraités, fichiers d'entreprises), ce qui limite la microsimulation et
l'estimation de certains comportements.

| Domaine | Source et jeu de données | Période, fréquence | Usage | Qualité, limites |
|---|---|---|---|---|
| Comptes nationaux par branche | Eurostat `nama_10_a64`, `nama_10_a64_e`, `nama_10_a64_p5` (comptes de l'Insee) | 1995-2025, annuel | équations d'emploi, de prix, d'investissement | comptes semi-définitifs pour 2023-2025, révisables |
| Comptes des secteurs | Eurostat `nasa_10_nf_tr`, `nasa_10_f_bs`, `nasa_10_f_tr` | 1995-2025, annuel | ménages, sociétés, administrations ; bilans | sociétés financières peu détaillées |
| Finances publiques | Eurostat `gov_10a_main`, `gov_10dd_edpt1` (dette de Maastricht) | 1995-2025 | recettes, dépenses, dette | recoupé avec l'Insee |
| Tableau entrées-sorties | Insee, TES symétrique 64 produits | année de base | prix de Leontief, contenus en importations | structure figée sur l'année de base |
| Chômage | Insee, BDM, série 001688526 (BIT, trimestriel) | 1975-2026 | Phillips, Okun | — |
| Population | Insee, projections 2026 (29 scénarios), recensement 2022 (fichier détail) | 1962-2070 | démographie, population de microsimulation | projections conditionnelles |
| Activité par âge | Eurostat `lfsa_argan` (enquête Emploi) | 2003-2025 | activité des seniors (M9) | échantillon d'enquête |
| Retraites | Eurostat `spr_pns_ben`, `spr_exp_pens` ; LFSS 2026 (durées) ; DREES, CNAV (carrières longues) | 2000-2024 | M9 | pas de données individuelles |
| Impôt sur le revenu | DGFiP, IRCOM 2025 (revenus 2024), déclarations 2042 nationales, déciles | 2006-2024 | population M4, calage | agrégats par tranche |
| Taux d'intérêt | Eurostat `irt_lt_mcby_a/m`, `irt_st_m` ; BCE, séries MIR (crédits nouveaux) | 1980-2026 | M24 | — |
| Prévisions | FMI, World Economic Outlook (millésimes) | 2010-2031 | référence, validation ex ante | — |
| Législation | OpenFisca-France 177.0.0 ; textes (CGI, CSS, LFSS 2026) | 2026 | microsimulation, règles | moteur communautaire |

Données indisponibles et substitutions principales : potentiel en temps réel (reconstruit par filtrage), patrimoine
des ménages par ménage (approché par les revenus du patrimoine), héritages reçus (assiette pondérée par l'âge),
transitions individuelles emploi-chômage (probabilités moyennes), durées validées individuelles (effets moyens par
génération dans M9).

## Typologie des paramètres {#sec:typologie}

Le registre complet figure en annexe \ref{sec:annexe-a}. Le tableau suivant classe les paramètres les plus influents.

| Catégorie | Exemples | Nombre approximatif | Conséquence |
|---|---|---|---|
| **Estimés économétriquement** [E] | accélérateur (0,67), élasticité de la consommation au revenu (0,85) et vitesse de retour (0,22), indexation des salaires (0,39), élasticités du commerce, règle de la BCE, transmission aux crédits, prime souveraine, activité des seniors, vitesse du taux apparent des sociétés (0,60) | plusieurs dizaines (dont 25 effets fixes de branche) | intervalles d'incertitude disponibles |
| **Calibrés sur la littérature** [C] | $\sigma = 0{,}45$, pente de Phillips (−0,004), pente des prix (0,10), épargne de précaution (0,3), effet du taux réel (0,2), incidences fiscales, élasticités des hauts revenus, capital public (0,08) | une trentaine | variantes basse et haute systématiques |
| **Issus de la littérature, appliqués tels quels** [E, littérature] | report de l'âge de départ par année de durée requise (9 mois / 5 mois, Bozio 2011) ; répercussion asymétrique de la TVA (Benzarti et al., 2020) | quelques-uns | dépendent de la transposabilité |
| **Hypothèses de scénario** [H] | règle budgétaire (α, β, d*), convention de dépense, OAT de référence, durée des contentieux européens, compositions des enveloppes non ventilées, additionnalité de l'investissement hors budget | une vingtaine | présentées en variantes |
| **Fragiles ou insuffisamment identifiés** | $\sigma$, Phillips, fermeture (ρ), coefficient de solde de la prime souveraine, élasticité de l'investissement au coût d'usage (−0,18), effet de l'assurance chômage sur u* | — | priorité des analyses de sensibilité |

## Méthodes d'estimation {#sec:methodes}

**Équations de comportement (M7).** Modèles à correction d'erreur estimés en une étape (relation de long terme et
dynamique de court terme ensemble), sur 1997-2019 hors années de crise sanitaire. Les équations de branche sont
estimées en panel de 25 branches avec effets fixes, par moindres carrés pondérés par la taille de la branche, avec des
écarts types groupés par année ; les équations agrégées par moindres carrés ordinaires avec écarts types robustes à
l'autocorrélation (Newey-West). Lorsque la théorie l'impose et que la version libre est biaisée par la colinéarité,
des contraintes sont imposées (homogénéité de long terme des prix, rendements constants de l'emploi), et le résultat
libre est publié.

**Pourquoi 1997-2019 ?** L'échantillon commence avec les séries homogènes des comptes nationaux et s'arrête avant la
crise sanitaire, dont les mouvements (activité partielle, épargne forcée, aides massives) ne relèvent pas des
comportements ordinaires. Les équations de taux d'intérêt font exception (estimées jusqu'en 2024, seul épisode de
hausse des taux de l'échantillon). Conséquence : le modèle décrit des comportements d'une période de taux en baisse et
d'inflation faible ; leur stabilité dans un environnement de taux élevés n'est pas garantie (critique de Lucas).

**Fermeture (ρ, θ).** Inférence indirecte : on choisit les valeurs qui reproduisent la durée moyenne des écarts de
production observée dans les données AMECO et FMI (1982-2019), et la réaction de la consommation à un choc permanent
(Blundell, Pistaferri et Preston, 2008).

**Activité des seniors (M9).** Moindres carrés non linéaires sur les taux d'activité par tranche quinquennale et par
sexe (2003-2019), pondérés par la population ; test hors échantillon sur 2020-2025.

**Politique monétaire (M24).** Règle de la BCE et transmission au taux allemand : moindres carrés sur données annuelles
de la zone euro ; crédits : ajustement partiel sur les séries MIR ; prime souveraine : panel de pays de la zone euro à
effets fixes, avec et sans 2010-2013.

**Paramètres non identifiés.** Quand une estimation libre est non significative, de signe opposé à la théorie, ou
instable selon l'échantillon, le paramètre est calibré au milieu de la littérature et reçoit des variantes. Règle de
méthode appliquée dans tout le projet : **aucun paramètre n'est choisi pour améliorer une simulation particulière**,
et une spécification n'est pas retenue sur le seul critère de l'erreur quadratique.

## Calibration de la référence {#sec:calibration}

La trajectoire de référence à politique inchangée est construite en trois temps : (i) les constantes de branche sont
recalées sur les résidus moyens des dernières années observées (2023-2025) au lieu d'extrapoler les effets fixes
estimés ; (ii) les exogènes reproduisent les prévisions du FMI jusqu'en 2031 (croissance, inflation, demande mondiale) ;
(iii) au-delà, les hypothèses de long terme (productivité, chômage structurel, démographie centrale de l'Insee) sont
prolongées. La convention de dépense publique « part constante » fait croître la consommation publique et les
prestations hors pensions comme le PIB potentiel conventionnel.

**Une référence explosive.** Avec l'OAT à 4,89 % (dernier point mensuel observé) maintenue, la référence voit le taux
apparent de la dette passer de 2,0 % en 2025 à 4,0 % en 2032 et 4,6 % en 2047, alors que la croissance nominale
ralentit (de 2,9 % à 1,8 %) : le différentiel taux-croissance devient positif et la dette atteint 139 % du PIB en
2032 et 262 % en 2047 sans règle budgétaire (R0), le déficit passant de 5,1 % à 8,2 % puis 16,3 % du PIB. La charge
d'intérêts explique l'essentiel de la dérive (de 2,3 à 5,3 points de PIB en 2032 et 11,4 points en 2047) ; le solde
primaire se dégrade beaucoup moins (de −2,8 à −2,9 points en 2032, −4,9 points en 2047). **Cette référence n'est
pas une prévision** : elle décrit ce que produirait l'absence de toute correction, avec des taux élevés maintenus. Elle
a deux conséquences pour l'étude : les effets des programmes se lisent en écart à cette référence et sous règle
budgétaire ; et la lecture par objectifs budgétaires (lecture B) mesure un effort *par rapport à cette dérive*, ce qui
la rend sensible à l'hypothèse de taux. Une variante avec l'OAT à sa moyenne des douze derniers mois (3,82 %) est
présentée systématiquement.

**Revalidation de l'environnement.** Chaque environnement calibré est mis en cache avec une empreinte de tous ses
paramètres (coefficients estimés, constantes des modules, paramètres globaux, cibles de calibration, exogènes
calibrées) et une trajectoire de contrôle d'environ 70 variables. À chaque chargement, si l'empreinte diffère, le
modèle resimule la référence ; il n'accepte le cache que si toutes les trajectoires sont identiques à $10^{-9}$ près et
si les paramètres calibrés n'ont pas changé ; sinon il recalibre. Un test vérifie qu'un coefficient modifié est
refusé.

## Validation : rétrosimulations et comparaisons {#sec:validation}

La validation d'un modèle macroéconomique se fait à plusieurs niveaux, du plus faible au plus exigeant.

**Niveau 1 — équation par équation.** Chaque équation est simulée dynamiquement hors échantillon (estimation
1997-2012, simulation 2013-2019 ; estimation 1997-2019, simulation 2022-2024). Les équations battent une prévision
naïve (tendance prolongée) pour la consommation, les salaires, les importations, les exportations et l'emploi
(2022-2024) ; elles font moins bien pour les prix de la valeur ajoutée (2013-2019) et pour l'investissement des sociétés
(erreur de niveau de +11 % en 2024).

**Niveau 2 — rétrosimulation conditionnelle du modèle complet.** Le modèle est simulé sur une période passée avec les
exogènes observées. Écarts en dernière année (simulé − observé), configuration P4 :

| Période | PIB (%) | Prix à la consommation (%) | Emploi (%) | Chômage (pt) | Dette (pt de PIB) |
|---|---|---|---|---|---|
| 2010 → 2019 | +1,64 | +1,36 | +1,66 | −1,52 | −4,64 |
| 2014 → 2019 | −0,42 | −1,53 | +0,27 | −0,25 | −1,77 |
| 2019 → 2024 | +0,90 | −3,20 | −1,65 | +1,53 | −5,93 |

Les erreurs de croissance annuelle sont faibles ; les erreurs de niveau s'accumulent sur dix ans, et l'épisode
inflationniste de 2022-2023, hors du domaine d'estimation, est mal reproduit (prix sous-estimés de 3,2 %).

**Niveau 3 — prévision ex ante.** Le modèle est utilisé comme il l'aurait été à l'époque, avec les seules informations
disponibles (millésimes du FMI des années 2010-2016). Erreur absolue moyenne sur la croissance : 0,39 point à un an et
0,25 point à cinq ans, contre 0,59 et 0,34 pour le FMI du même millésime et 0,84 et 0,38 pour une prévision naïve.
Sur l'inflation, le modèle fait moins bien que le FMI (0,72 contre 0,43 à un an). Sur la dette, il présente un biais
de +10,6 points à cinq ans, dû à la convention de législation inchangée (le gouvernement corrige toujours une partie
de la dérive).

**Niveau 4 — choc de politique identifié.** Le crédit d'impôt pour la compétitivité et l'emploi (CICE, 2013-2018) est
simulé rétrospectivement (avec et sans, coût budgétaire compté) : +71 000 emplois marchands en 2016 et +86 000 en
2017, contre environ 100 000 dans les évaluations microéconométriques (2013-2016) et environ 160 000 dans une évaluation
macro-sectorielle (2013-2017), selon la synthèse de France Stratégie (2020). Le modèle est dans l'ordre de grandeur,
plutôt en dessous, ce qui est cohérent avec une transmission aux prix plus forte que celle mesurée ex post.

## Ce que prouvent les tests automatisés — et ce qu'ils ne prouvent pas {#sec:tests}

Le projet comprend des suites de tests automatisés (annexe \ref{sec:annexe-f}) : 32 tests pour les phases 4.3 à 6,
6 tests pour la finalisation (retraites, lecture par objectifs, corpus), 142 contrôles d'intégration comptable, et les
suites antérieures (versions 0.8 et 0.9).

**Ce qu'ils prouvent.**

- **Cohérence comptable** : les identités entre secteurs, entre flux et stocks, entre coûts et prix sont respectées
  à la précision numérique (écart relatif de l'ordre de $10^{-16}$ sur l'identité dette-solde des simulations de
  programmes).
- **Reproductibilité** : les versions antérieures (0.8, 0.9) et la référence sans règle sont reproduites exactement ;
  un environnement mis en cache n'est accepté que si ses paramètres et ses trajectoires sont inchangés.
- **Absence de régression** : une modification du code n'altère pas les résultats des configurations qu'elle ne vise
  pas.
- **Conformité des traductions** : les conversions entre montants annoncés et paramètres du modèle inversent
  exactement les rendements statiques ; les totaux publiés par LFI (106,4 Md€ et 81,7 Md€) sont recoupés ; les
  calendriers légaux de durée d'assurance sont respectés ; les variantes européennes agissent comme spécifié.
- **Sens des effets** : les réformes des retraites ont l'effet attendu sur la population active (durée plus courte,
  départs anticipés → moins d'actifs ; âge et durée plus élevés → plus d'actifs).

**Ce qu'ils ne prouvent pas.**

- Ils ne prouvent pas que **les paramètres sont justes** : un modèle peut être parfaitement cohérent et se tromper
  de multiplicateur.
- Ils ne prouvent pas que **les comportements estimés sur 1997-2019** resteront valables dans un environnement de
  taux élevés, après des réformes de grande ampleur (critique de Lucas).
- Ils ne prouvent pas que **la traduction d'un programme** reflète les intentions du candidat : elle reflète un texte
  publié, complété d'hypothèses explicitées.
- Ils ne constituent pas une **validation scientifique** au sens d'une confrontation réussie à des expériences
  indépendantes : seuls les niveaux 2 à 4 ci-dessus s'en approchent, et leurs résultats sont mitigés (bonne
  performance sur la croissance, moins bonne sur les prix et l'investissement).

Cette distinction est essentielle : la cohérence et la reproductibilité sont des conditions nécessaires, pas
suffisantes, de la crédibilité des résultats.

## Choix techniques écartés {#sec:ecartes}

- **Pas trimestriel.** Examiné en phase 5 et non retenu : les mesures sont annuelles, les horizons de 5 ans et plus, et
  les équations trimestrielles disponibles ne couvrent que les salaires et les prix marchands ; leur généralisation
  aurait demandé une recalibration complète sans gain démontré pour la comparaison.
- **Contenu importé selon le niveau de vie, tension des capacités sur les importations, taux d'intérêt dans
  l'équation de logement** : testés, non retenus (effets non significatifs ou oscillations non observées).
- **Équation de Lintner pour les dividendes** : non identifiée ; règle proportionnelle retenue.
- **Effet du taux légal de l'impôt sur les sociétés sur l'assiette** : élasticité historique non significative
  (−0,10 ± 0,29) ; le taux apparent observé est utilisé en rétrosimulation.
