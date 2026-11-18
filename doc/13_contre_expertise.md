# Contre-expertise scientifique et analyse de robustesse (version 0.6, 18 novembre 2026)

Objet : chercher les situations où le modèle 0.5 produit des résultats erronés, fragiles ou dépendants d'hypothèses
mal identifiées, et mesurer ce que ses conclusions sur les programmes permettent réellement d'affirmer. Démarche :
registre des paramètres, tests de mécanismes, sensibilités univariées, criblage multivarié de Morris, tirages
statistiques des coefficients estimés, scénarios cohérents, validation hors échantillon. Le code n'a été modifié que
pour des erreurs caractérisées (section 8). La version 0.5 reste reproductible (étiquette git `v0.5`).

Livrables : ce rapport ; registre des paramètres (14_registre_parametres.md, outputs/registre_parametres.csv) ;
tableau de robustesse des programmes (outputs/robustesse_programmes.md, repris en section 6) ; tests discriminants
(outputs/tests_discriminants.md) ; validation hors échantillon (outputs/validation_hors_echantillon.md) ; contenu
domestique de la consommation par quintile (outputs/contenu_consommation_quintiles.md) ; dispositif de sensibilité
réutilisable (simulateur/sensibilite.py, tests/contre_expertise.py, tests/synthese_contre_expertise.py).

## 1. Principaux enseignements

1. **Le facteur décisif n'est pas un coefficient estimé mais une hypothèse de bouclage.** La « fermeture d'offre »
   (rythme auquel l'économie ramène le chômage vers son niveau structurel : politique monétaire, crédit,
   compétitivité) est le premier facteur d'incertitude sur le PIB et l'emploi pour les six programmes (criblage de
   Morris). Elle n'est pas estimée ; sa plage (0 à 0,4) couvre des visions keynésienne et classique du moyen terme.
2. **Les effets de court terme (2028) sont plus robustes que ceux de 2032.** Les multiplicateurs de première année
   dépendent de coefficients estimés relativement stables ; les effets de fin de mandat dépendent de la fermeture
   d'offre et de la boucle prix-salaires.
3. **Le signe de l'effet sur le solde public est robuste ou plutôt robuste pour cinq programmes sur six** (robuste :
   Attal, Glucksmann ; plutôt robuste : Le Pen, Mélenchon, Philippe), fragile pour le programme de Bruno Retailleau, dont les économies de dépenses et leurs effets
   sur l'activité se compensent.
4. **L'effet sur le ratio de dette est fragile pour presque tous les programmes.** Il dépend du niveau des prix
   (dénominateur) et donc de la courbe de Phillips et de l'indexation des salaires, deux paramètres mal identifiés.
   Il ne faut pas tirer de conclusion sur la dette au-delà de l'effet sur le solde.
5. **Les réformes de l'âge de départ sont les mesures les plus incertaines** : elles modifient la population active,
   et leur effet sur le PIB et l'emploi dépend de la manière dont l'économie absorbe un choc d'offre de travail
   (étendue de 1,7 à 2,3 points de PIB en 2032 pour un retour à 60 ou 62 ans). Pour les programmes qui les combinent
   à une relance (Glucksmann, Mélenchon), le signe de l'effet sur le PIB en 2032 n'est pas établi.
6. **Effets robustes** : baisse du PIB et de l'emploi pour le programme de Marine Le Pen (retour immédiat à 62 ans et
   économies de dépenses) ; baisse de l'emploi et amélioration du solde pour celui de Gabriel Attal (baisse modérée du PIB : plutôt robuste) ; dégradation
   du solde et hausse du revenu national nominal pour ceux de Raphaël Glucksmann et Jean-Luc Mélenchon ; amélioration
   du solde et baisse du revenu national pour celui d'Édouard Philippe (signe du solde plutôt robuste).
7. **Erreurs trouvées** : un cumul erroné de l'effet du coût d'usage du capital (baisse d'IS et chocs de taux
   surestimés d'un facteur 3), un double compte du logement dans les rétrosimulations, et une erreur du premier
   dispositif de sensibilité (dérive de la référence) qui aurait fait conclure à tort à la prépondérance de
   l'élasticité de substitution. Les trois sont corrigées (section 8).
8. **Capacité prédictive** : hors chocs, le modèle prévoit mieux qu'un prolongement naïf l'investissement, les
   importations, l'emploi et les prix, mais pas la croissance du PIB ; il échoue sur 2022-2024 (emploi, prix), pour
   des raisons identifiées (productivité, prix de l'énergie et marges). Une partie de la bonne rétrosimulation
   2015-2019 de la version 0.5 venait de l'erreur sur le coût d'usage (investissement −0,4 % en v0.5, −4,9 % en v0.6
   en 2019).
9. **Les écarts entre programmes ne sont généralement pas plus grands que leurs plages de sensibilité** : le modèle
   ne permet pas de les ordonner sur le PIB ou l'emploi de 2032, sauf quand les plages ne se recouvrent pas (par
   exemple, l'effet sur le PIB du programme de Marine Le Pen est négatif dans toutes les configurations, celui de
   Gabriel Attal dans presque toutes, avec une ampleur plus faible).

## 2. Cartographie des incertitudes (registre)

Le registre classe 46 paramètres : 24 coefficients estimés sur données françaises (E), 6 calibrés sur données
françaises (C), 11 transposés de la littérature (L), 5 hypothèses conventionnelles (H). Constats :

- **Petits échantillons.** Les équations macroéconomiques sont estimées sur 23 observations annuelles (1997-2019). Sur
  24 coefficients suivis, 9 ont un t de Student inférieur à 2 : force de rappel de la consommation (t = −1,0),
  élasticités-prix des importations (t = −1,1 et −1,5), indexation des salaires sur les prix (t = 1,8), rappel des
  salaires vers la part salariale (t = −1,6), rappel du logement (t = −1,4), tension des capacités dans les prix
  (t = 1,7), revenus de la propriété (t = 1,1). Pour ces coefficients, les données ne permettent pas de rejeter
  l'absence du mécanisme : leur signe est imposé par la théorie, pas démontré par les données.
- **Contraintes de signe.** Les intervalles à ± 2 erreurs-types de 8 coefficients franchissent la borne théorique
  (rappel positif, donc dynamique explosive ; élasticité-prix positive). Ils sont tronqués dans les sensibilités. Parmi
  les tirages conjoints des coefficients, 55 % violent au moins une contrainte de signe et sont écartés : l'incertitude
  d'estimation jointe est plus large que ne le suggèrent les coefficients pris isolément.
- **Compensations.** Sept paires de coefficients d'une même équation sont corrélées à plus de 0,7 en valeur absolue :
  consommation (court terme et rappel, −0,82), importations (rappel et demande de long terme, −0,98), exportations
  (demande et prix, +0,86), salaires (prix et productivité, −0,83), revenus de la propriété. Leurs effets peuvent se
  compenser : une élasticité de court terme élevée s'accompagne d'un rappel faible. Les sensibilités univariées, qui
  les déplacent séparément, exagèrent l'incertitude de ces paires ; les tirages conjoints en tiennent compte.
- **Instabilité dans le temps** (section 7.2) : l'élasticité de court terme de la consommation passe de 1,15
  (1997-2007) à 0,54 (2003-2019) ; l'indexation des salaires de 0,73 à −0,06 ; le rappel de la consommation de −0,81
  à −0,03. Ces coefficients ne sont pas des constantes structurelles.
- **Paramètres non estimés les plus influents** : fermeture d'offre (H), courbe de Phillips (C, non identifiée sur
  données annuelles), élasticité de substitution capital-travail (L), profil des propensions à consommer (L),
  réactions des hauts revenus (L).

## 3. Examen des mécanismes

### 3.1 Consommation et épargne des ménages

- **Propension marginale et propension moyenne.** Le profil 0,90 → 0,40 est un profil de propensions marginales de
  première année. Les propensions moyennes observées par l'Insee pour 2022 (taux d'épargne de −29 % pour le premier
  quintile à 27 % pour le cinquième) sont compatibles avec ce profil : la propension marginale des ménages aisés (0,40 à
  0,53) est inférieure à leur propension moyenne (0,73), comme attendu ; celle des modestes (0,85-0,90) est inférieure
  à leur propension moyenne apparente (> 1), ce qui reflète les transferts et désépargnes non durables. Seul le profil
  relatif intervient dans le modèle ; le niveau moyen reste celui de l'équation estimée.
- **Permanent et temporaire.** L'équation agrégée (élasticité 0,85 la première année, 1 à long terme) est estimée sur
  des variations de revenu majoritairement durables. Elle surestime l'effet d'un revenu ponctuel (prime, chèque) : la
  littérature (Fagereng et al. 2021) donne environ 0,5 la première année pour un gain exceptionnel, et l'Insee (2019)
  0,5 après un an en moyenne sur données trimestrielles. Le modèle ne distingue pas les deux : **limite** (mesures
  ponctuelles surévaluées en effet de demande d'environ un tiers la première année).
- **Patrimoine, âge, dette.** La Banque de France (document de travail n° 962, 2024) montre une propension à consommer
  la richesse financière de plus de 0,11 pour les ménages sous la médiane de patrimoine et nulle pour le dernier
  décile ; l'épargne de précaution représente environ 6 % du flux d'épargne des actifs (Économie et Statistique
  n° 513). Les ménages « pauvres sans liquidité » (hand-to-mouth) représentent en France une part comparable à
  celle de l'Italie et de l'Espagne (20-30 %, HFCS). Le modèle ne représente ni l'âge, ni le patrimoine, ni la dette :
  l'hétérogénéité passe uniquement par le niveau de vie.
- **Instabilité.** L'élasticité de court terme de la consommation varie de 0,54 à 1,15 selon la période d'estimation,
  et la force de rappel n'est pas significative (t = −1,0). Ces deux paramètres sont corrélés (−0,82) : une forte
  élasticité de court terme va avec un rappel faible.
- **Sensibilité.** Profil plat, central ou accentué : le PIB de 2030 varie d'environ un tiers pour une mesure
  redistributive (RSA +25 % : +0,08 / +0,12 / +0,14 %). Test 1 (10 Md€) : transfert aux trois premiers déciles,
  consommation +0,84 % et PIB +0,17 % en 2032 ; baisse d'impôt des deux derniers déciles, +0,46 % et +0,09 %.
- **Effets d'anticipation** : absents (pas d'équivalence ricardienne, pas d'épargne de précaution liée au déficit).

### 3.2 Importations et contenu domestique de la consommation

Analyse entrées-sorties (tableau 2022, passerelle fonctions → produits avec marges et impôts ; structures de
consommation par quintile de l'Insee) : pour 1 € dépensé, impôts sur les produits 13,7 % (premier quintile) à 14,5 %
(cinquième), importations directes et indirectes 27,2 % à 28,1 %, valeur ajoutée produite en France 57,7 % à 55,8 %
(dont commerce et transport 9,5 à 10,5 %, industrie 6,1 à 5,7 %), 7,2 à 7,4 emplois pour 1 M€ dépensé.
Conclusion : les différences de composition sectorielle existent (logement et énergie chez les modestes, services
marchands et équipement chez les aisés) mais se compensent largement : 2 points de valeur ajoutée domestique et
3 % d'emplois au plus. Le coefficient agrégé de contenu importé n'est pas une source d'erreur importante pour les
mesures redistributives ; l'hétérogénéité d'épargne l'est davantage (facteur 1,8 entre les deux politiques du test 1).
Une approche par produit et par quintile serait plus juste mais ne changerait les résultats qu'au second ordre ; elle
n'est pas prioritaire. Limite : à l'intérieur d'une fonction (gamme, marque), les données ouvertes ne distinguent pas.

### 3.3 Distribution des bénéfices et fiscalité des entreprises

- **Détention étrangère.** Le CAC 40 (50 % de non-résidents) n'est pas représentatif : 36,7 % pour l'ensemble des
  actions cotées en 2022, environ 30 % hors CAC 40, nettement moins pour les sociétés non cotées et les PME (détention
  surtout familiale et par investissement direct). La valeur centrale passe de 0,40 à 0,30 (plage 0,20-0,50).
- **Affectation des bénéfices.** Test 4 (baisse de l'IS de 25 % à 20 %, gain statique 12,2 Md€) en 2032 : investissement
  majoritaire, PIB +0,20 % et RNB +13,7 Md€ ; distribution majoritaire, PIB +0,09 % et RNB +0,6 Md€ ; désendettement,
  trésorerie ou investissement à l'étranger, PIB +0,07 % et RNB +3,4 Md€ (hors revenus futurs des placements, non
  représentés). L'écart entre comportements porte surtout sur le RNB et la composition de la demande, peu sur le PIB.
- **Erreur corrigée** : l'effet du coût d'usage du capital se cumulait d'une année sur l'autre (section 8) ; la
  baisse d'IS produisait une hausse de l'investissement d'environ 3 % en 2035 au lieu de 0,9 %.
- **Non représenté** : R&D, rachats d'actions, salaires financés par les profits (partage de la valeur ajoutée), effet
  du taux de marge sur l'investissement (coefficient estimé, t = 1,4, non utilisé), différenciation entre entreprises
  cotées, non cotées, PME et filiales de groupes étrangers. Le modèle ne peut pas trancher si une baisse d'IS finance
  l'investissement : il en donne la fourchette (test 4).

### 3.4 Salaires, emploi et compétitivité

Hausse uniforme de 2 % (test 5a, version 0.6, 2032) : PIB +0,01 %, emploi −39 000. Décomposition (audit v0.5, 2030) :
coût du travail et substitution −54 000 ; demande induite +35 000 ; boucle prix-salaires −5 000 ; compétitivité-prix :
exportations −0,6 %. Contre-expertise :
- **Substitution capital-travail** (σ = 0,4, transposé) : 0,2 à 0,7 dans la littérature ; l'emploi après choc de coût
  varie d'environ ± 25 000 (Mélenchon : +24 000 à −41 000 en 2032).
- **Marges** (test 5e) : si les prix ne répercutent pas le coût salarial, l'emploi baisse davantage (−68 000) car le
  coût réel du travail augmente plus ; aucun mécanisme ne relie la baisse des marges à l'investissement (limite).
- **Ciblage** : même masse salariale, bas salaires (déciles 1-4) : PIB +0,13 %, emploi +3 000 ; intermédiaires :
  +0,06 % et −20 000 ; uniforme : +0,01 % et −39 000. Seule la propension à consommer distingue ces variantes : les
  équations de salaires et d'emploi sont agrégées. Le modèle ne représente ni l'élasticité plus forte de l'emploi peu
  qualifié au coût du travail (littérature : Kramarz et Philippon 2001 ; évaluations des allègements), ni les
  allègements dégressifs : **la hausse ciblée sur les bas salaires est probablement trop favorable** dans le modèle.
- **Secteurs exposés et abrités** : les prix de VA et l'emploi sont estimés par branche, mais avec des coefficients
  communs ; la compétitivité-prix n'agit que sur les exportations agrégées. Distinction sectorielle insuffisante.
- **Élasticités** : exportations −0,59 (t = −3,5), conforme aux estimations françaises (−0,4 à −0,8) ; importations
  −0,11 (non significative), plus faible que la littérature (−0,3 à −0,6). Le modèle sous-estime probablement la perte
  de parts de marché intérieures après une hausse des coûts.

### 3.5 Dépenses publiques et multiplicateurs

Contrôle « dépense publique +1 point de PIB » (section 5) : multiplicateur de 1,0 la première année (effet direct),
1,28 avec la consommation induite, 0,78 après fermeture d'offre. Cette séquence est cohérente avec les multiplicateurs
de Mésange et de FR-BDF (0,8 à 1,2 la première année, décroissants). Selon la nature de la dépense (tests 2 et 5d,
10 Md€ ou équivalent, 2032) : consommation des ménages (baisse de l'épargne) PIB +0,15 %, investissement public avec
effet d'offre +0,18 % (+0,13 % sans effet d'offre), rémunérations publiques +2 % +0,10 %. Seul l'investissement public
améliore le potentiel (élasticité 0,08, plage 0,04-0,12) ; aucune autre dépense (éducation, recherche, subventions)
n'a d'effet d'offre représenté. Les prestations sociales et les rémunérations publiques ne se distinguent que par la
propension à consommer des bénéficiaires et par leur effet direct sur la valeur ajoutée non marchande.

### 3.6 Contraintes d'offre et capacités productives

Le modèle comporte : un taux d'utilisation des capacités dans les prix de l'industrie (coefficient non significatif,
t = 1,7), une contrainte agrégée de « fermeture d'offre » (hypothèse), un délai de construction des capacités pour la
réindustrialisation. Il ne comporte ni contraintes de qualification, ni délais de formation, ni contrainte énergétique
ou logistique. Ces contraintes ne sont pas identifiables sur les données disponibles (le taux d'utilisation n'explique
pas les importations, audit v0.5). Elles sont représentées par des scénarios : la fermeture d'offre (0 à 0,4) joue ce
rôle et apparaît comme **le facteur le plus influent** pour presque tous les programmes (section 6). Son effet dépend
de la nature des mesures : les réformes de l'âge de départ, qui réduisent la population active, ont des effets dont le
signe peut s'inverser selon que l'économie absorbe ou non le choc d'offre de travail.

### 3.7 Chocs énergétiques

Test 6 (2032) : énergie importée +50 %, PIB −1,04 %, emploi −323 000, RNB −26 Md€, solde extérieur −3,2 points ;
électricité et gaz produits en France +50 % (marge de la branche D), PIB −0,10 %, RNB +23 Md€ (le gain des producteurs
compense la perte des ménages en valeur), dette −0,7 point (inflation). L'énergie produite en France transfère du revenu
entre agents résidents ; l'énergie importée appauvrit la Nation. Limite : le profit supplémentaire des producteurs
(dont l'État actionnaire) n'est pas redistribué explicitement.

## 4. Dispositif d'analyse de sensibilité

- **Facteurs** : 22, dont 12 coefficients estimés (bornes : ± 2 erreurs-types, tronquées aux contraintes de signe),
  θ (transmission des prix d'importation), 9 paramètres calibrés, transposés ou conventionnels (bornes : plages
  plausibles documentées dans le registre).
- **Sensibilités univariées** : chaque facteur à sa borne basse puis haute, les autres au centre.
- **Criblage de Morris** (Morris 1991 ; Campolongo, Cariboni et Saltelli 2007) : 6 trajectoires de 23 points sur une
  grille à 4 niveaux (138 simulations par scénario) ; indices μ* (importance) et σ (interactions, non-linéarités). La
  méthode de Sobol, qui fournirait des parts de variance, demanderait plusieurs milliers de simulations par scénario
  (N(k+2) avec N ≥ 500 et k = 22) et supposerait des lois de probabilité que la plupart des facteurs n'ont pas ; Morris
  est la méthode de criblage recommandée pour un modèle coûteux et un grand nombre de facteurs mal documentés.
- **Incertitude statistique** : 50 tirages conjoints de tous les coefficients estimés (loi normale de covariance
  estimée), tirages violant les contraintes de signe écartés ; intervalle 5e-95e centiles. Elle ne couvre ni la
  spécification, ni les paramètres calibrés.
- **Scénarios cohérents** : « demande forte (keynésien) », « offre contrainte (classique) », « économie très
  ouverte », « réactions fortes des ménages aisés et des entreprises », « réactions faibles » (définitions dans
  simulateur/sensibilite.py).
- **Présentation** : intervalle statistique et plage de sensibilité sont présentés séparément ; aucune probabilité
  n'est attribuée à la plage de sensibilité. Les configurations instables (dette > 25 points ou PIB > 10 % d'écart),
  produites par certaines combinaisons de paramètres, sont écartées et comptées.
- **Approximations** : la référence est re-simulée avec les paramètres modifiés mais n'est pas re-calée ; les
  rétroactions de la zone euro sont calculées au jeu central et mises à l'échelle (facteur « europe »). Contrôle :
  au jeu central, le dispositif reproduit exactement le simulateur.

## 5. Variantes de contrôle

Variantes élémentaires soumises au même dispositif (mesure en 2028 ; central [plage] signe, 2032) :

| Scénario | PIB (%) | Emploi (milliers) | Solde (pt) | Dette (pt) | RNB (%) |
|---|---|---|---|---|---|
| contrôle : age | -1.14 [-2.40 ; +0.34] fragile | -251 [-496 ; +92] fragile | -0.39 [-0.80 ; +0.39] fragile | -0.07 [-6.84 ; +3.56] fragile | +1.10 [-1.18 ; +5.80] fragile |
| contrôle : depense | +0.58 [-0.03 ; +1.36] plutôt robuste | +204 [+70 ; +406] plutôt robuste | -0.39 [-0.61 ; +0.08] plutôt robuste | -0.24 [-4.57 ; +1.78] fragile | +1.82 [+0.59 ; +4.82] plutôt robuste |
| contrôle : emploi_public | -0.16 [-0.26 ; -0.08] plutôt robuste | -46 [-69 ; -31] plutôt robuste | +0.07 [+0.01 ; +0.10] plutôt robuste | +0.12 [-0.07 ; +0.54] fragile | -0.27 [-0.55 ; -0.15] plutôt robuste |
| contrôle : is | +0.08 [+0.02 ; +0.18] robuste | +18 [+5 ; +40] robuste | -0.63 [-0.72 ; -0.56] robuste | +2.64 [+2.37 ; +2.95] robuste | +0.04 [-0.10 ; +0.23] indéterminé |
| contrôle : rsa | +0.08 [+0.02 ; +0.23] plutôt robuste | +29 [+13 ; +72] robuste | -0.10 [-0.16 ; +0.02] plutôt robuste | +0.20 [-0.90 ; +0.60] fragile | +0.22 [+0.08 ; +0.85] robuste |
| contrôle : tva | -0.12 [-0.32 ; +0.00] plutôt robuste | -48 [-104 ; -17] plutôt robuste | +0.48 [+0.36 ; +0.66] robuste | -2.05 [-3.78 ; -0.58] robuste | -0.10 [-0.88 ; +1.03] fragile |

Lecture : la baisse d'IS a des effets faibles mais robustes (PIB +0,08 %, solde −0,63 point) ; la TVA (+2 points)
améliore le solde de façon robuste ; la dépense publique (+30 Md€, environ 1 point de PIB) a un multiplicateur de 1,26 en
2028 qui tombe à 0,58 en 2032 (1,25 sans fermeture d'offre, 0,13 avec une fermeture forte) ; le retour à 62 ans
(contrôle « age ») a des effets fragiles sur tous les indicateurs.

## 6. Robustesse des programmes

Tableau de synthèse (2032 ; central [plage de sensibilité] robustesse du signe). Détail par candidat, horizons 2028,
2030 et 2032, intervalles statistiques, paramètres dominants et mesures responsables de l'incertitude :
outputs/robustesse_programmes.md (reproduit dans l'interface pour chaque candidat).

| Scénario | PIB (%) | Emploi (milliers) | Solde (pt) | Dette (pt) | RNB (%) |
|---|---|---|---|---|---|
| Gabriel Attal | -0.28 [-0.55 ; -0.12] plutôt robuste | -83 [-149 ; -48] robuste | +0.26 [+0.08 ; +0.37] robuste | -0.26 [-0.89 ; +1.17] fragile | -0.52 [-1.36 ; -0.27] robuste |
| Raphaël Glucksmann | -0.22 [-1.61 ; +1.51] fragile | -157 [-438 ; +265] fragile | -1.57 [-2.23 ; -0.56] robuste | +3.99 [-4.68 ; +8.28] fragile | +2.05 [-0.34 ; +8.16] plutôt robuste |
| Marine Le Pen | -1.62 [-2.29 ; -0.85] robuste | -439 [-554 ; -276] robuste | -0.24 [-0.48 ; +0.16] plutôt robuste | +1.52 [-1.36 ; +3.29] fragile | -1.03 [-2.18 ; +0.73] fragile |
| Jean-Luc Mélenchon | -0.98 [-2.99 ; +1.63] fragile | -177 [-555 ; +455] fragile | -1.17 [-2.03 ; +0.37] plutôt robuste | +0.21 [-12.60 ; +7.88] fragile | +3.86 [+0.03 ; +12.78] plutôt robuste |
| Édouard Philippe | -0.17 [-0.96 ; +0.45] fragile | -72 [-252 ; +49] fragile | +0.41 [-0.01 ; +0.61] plutôt robuste | +0.32 [-1.46 ; +3.76] fragile | -1.18 [-3.33 ; -0.13] plutôt robuste |
| Bruno Retailleau | -0.93 [-2.22 ; +0.08] plutôt robuste | -321 [-643 ; -106] plutôt robuste | +0.33 [-0.48 ; +0.68] fragile | +2.40 [-0.93 ; +9.62] plutôt robuste | -3.04 [-7.35 ; -1.13] plutôt robuste |

Pour chaque candidat (2032) :

- **Gabriel Attal** : PIB −0,28 % (plage −0,55 à −0,12), emploi −83 000, solde +0,26 point : signes robustes ; dette
  fragile. Mesure principale d'incertitude : suppression de 100 000 emplois publics. Non évaluable : système universel
  par points, capitalisation, réformes des arrêts maladie et de l'assurance chômage.
- **Raphaël Glucksmann** : solde −1,57 point (robuste), revenu national +2 % (plutôt robuste) ; PIB −0,22 % mais de
  −1,6 à +1,5 % selon les hypothèses (fragile) : la relance par l'investissement (+0,73 % de PIB, seule) est compensée
  par le retour à 62 ans (−1,04 %, étendue 1,7 point). En 2028, PIB +1,12 % (positif dans presque toutes les
  configurations).
- **Marine Le Pen** : PIB −1,62 % (−2,3 à −0,9) et emploi −439 000 (−554 000 à −276 000) : signes robustes ; solde
  plutôt robuste (−0,24 point), dette et RNB fragiles. Mesures dominantes : retour immédiat à 62 ans (PIB −1,14 %,
  étendue 1,8 point) et économies de fonctionnement (−0,56 %). Non évaluable : économies liées à l'immigration au-delà
  des prestations (15 à 29 Md€ annoncés), règle d'or, capitalisation.
- **Jean-Luc Mélenchon** : solde −1,17 point (plutôt robuste), revenu national +3,9 % (plutôt robuste), prix plus
  élevés (robuste) ; PIB −0,98 % mais de −3,0 à +1,6 % (fragile), +0,80 % en 2028. Mesures dominantes : retraite à
  60 ans (étendue 2,3 points de PIB, 9 points de dette) et point d'indice +10 %. Non évaluable : blocage des prix,
  sécurité sociale intégrale, cotisation sur le capital, planification écologique.
- **Édouard Philippe** : solde +0,41 point (plutôt robuste), revenu national −1,2 % ; PIB −0,17 % (fragile, de −0,96
  à +0,45 %). Le recul de l'âge à 65 ans accroît l'offre de travail : son effet est positif à moyen terme mais dépend
  de la fermeture d'offre. Non évaluable : allocation familiale unique, réduction d'impôt pour les familles,
  capitalisation, 45 années de cotisation.
- **Bruno Retailleau** : PIB −0,93 % (plutôt robuste), emploi −321 000 (plutôt robuste), revenu national −3 % ; solde
  +0,33 point mais fragile (−0,48 à +0,68) : les économies (400 000 emplois publics, assurance chômage, fonctionnement)
  réduisent l'activité et donc les recettes. Non évaluable : décote de 7 % par an avant 65 ans (42 Md€ cumulés
  annoncés), capitalisation, 15 Md€ d'économies non détaillées.

Les mesures non représentées sont listées pour chaque candidat ; elles sont souvent parmi les plus importantes
budgétairement (retraites par points ou avec décote, immigration, blocage des prix). Les jeux de mesures sont donc
incomplets, et chacun d'une manière différente.

## 7. Validation historique

### 7.1 Rétrosimulations hors échantillon

Les coefficients sont estimés jusqu'à l'origine (2019 au plus), les exogènes sont observées (demande et prix mondiaux,
prix d'importation par produit, consommation publique, FBCF publique, population active, chômage structurel, taux
long, taux d'IS, prestations) : ces variables, injectées, ne valident rien. Sont prédits : PIB, consommation,
investissement, échanges, emploi, chômage, prix, salaires, finances publiques.

| Origine (simulation) | PIB : RMSE modèle / naïf | Consommation | Investissement | Importations | Emploi | Prix | Chômage en fin (points) |
|---|---|---|---|---|---|---|---|
| 2012 (2013-2016) | 0,74 / 0,50 | 1,01 / 0,64 | 1,67 / 1,99 | 0,89 / 2,95 | 0,32 / 0,37 | 0,94 / 0,85 | +0,5 |
| 2014 (2015-2018) | 0,64 / 0,50 | 0,49 / 0,73 | 1,55 / 2,44 | 0,85 / 0,99 | 0,32 / 0,53 | 0,29 / 0,74 | +0,1 |
| 2016 (2017-2019) | 0,64 / 1,16 | 0,09 / 0,57 | 2,69 / 3,34 | 1,52 / 1,05 | 0,39 / 0,71 | 0,40 / 0,87 | +1,1 |
| 2019 (2020-2022) | 4,13 / 6,07 | 6,35 / 5,55 | 5,36 / 6,68 | 5,63 / 10,08 | 0,73 / 1,40 | 0,50 / 2,42 | +1,4 |
| 2021 (2022-2024) | 1,50 / 1,06 | 2,36 / 2,02 | 1,29 / 3,19 | 1,73 / 4,75 | 1,14 / 0,69 | 2,66 / 4,11 | +3,1 |

(RMSE des croissances annuelles, points de pourcentage ; « naïf » : croissance moyenne des cinq années précédentes ;
résultats complets, dont AR(1) : outputs/validation_hors_echantillon.md.)

Constats :
- Hors chocs, le modèle bat le prolongement naïf pour l'investissement, les importations, l'emploi et les prix, mais
  **pas pour la croissance du PIB** (2012, 2014, 2021) : conditionnellement aux exogènes observées, ses mécanismes
  n'améliorent pas la prévision de l'activité agrégée sur 3-4 ans. Le modèle AR(1) fait mieux que lui pour le PIB à
  toutes les origines sauf 2019.
- **Crise sanitaire** : rupture de régime (confinements) que le modèle ne peut pas représenter ; son avantage apparent
  vient des exogènes observées (demande mondiale, consommation publique).
- **2022-2024** : emploi sous-estimé de 3,3 % et chômage surestimé de 3,1 points en 2024 ; prix sous-estimés de 5,4 %.
  Deux phénomènes non représentés : la baisse de la productivité apparente du travail (rétention de main-d'œuvre,
  apprentissage, composition), et la formation des prix de l'énergie et des marges (électricité +114 % de prix de VA
  en 2023, agroalimentaire +30 %). Le test 6b montre que le nouvel outil de marge par branche peut représenter ce
  canal en scénario, mais il n'est pas estimé.
- **Crise de 2008** : non testée, les tableaux entrées-sorties nécessaires (2007-2009) ne sont pas disponibles dans les
  sources ouvertes utilisées (premier tableau : 2010).

### 7.2 Stabilité des coefficients

| Coefficient | 1997-2007 | 1997-2012 | 1997-2019 (retenu) | 2003-2019 | 1997-2024 |
|---|---|---|---|---|---|
| Consommation, court terme | 1,15 (0,33) | 1,04 (0,23) | 0,85 (0,21) | 0,54 (0,10) | 1,08 (0,31) |
| Consommation, rappel | −0,81 (0,30) | −0,30 (0,22) | −0,22 (0,21) | −0,03 (0,12) | −0,26 (0,10) |
| Importations, demande | 1,50 (0,07) | 1,45 (0,10) | 1,46 (0,09) | 1,34 (0,07) | 1,23 (0,10) |
| Importations, rappel | −1,87 (0,16) | −0,90 (0,18) | −0,66 (0,15) | −0,68 (0,28) | −0,34 (0,24) |
| Exportations, prix | −0,43 (0,34) | −0,69 (0,37) | −0,59 (0,17) | −0,70 (0,24) | −0,68 (0,17) |
| Salaires, indexation | 0,73 (0,13) | 0,47 (0,25) | 0,39 (0,22) | −0,06 (0,12) | 0,37 (0,15) |
| Salaires, rappel | −0,38 (0,13) | −0,02 (0,06) | −0,09 (0,06) | −0,17 (0,05) | −0,05 (0,06) |
| Investissement SNF, accélérateur | 2,39 (0,32) | 2,44 (0,33) | 1,95 (0,33) | 2,04 (0,40) | 1,04 (0,29) |
| Investissement SNF, coût d'usage | −0,07 (0,01) | −0,07 (0,02) | −0,07 (0,02) | −0,05 (0,05) | −0,04 (0,02) |

Les élasticités de la demande d'importations et l'effet du coût d'usage sont stables ; la consommation et les salaires
ne le sont pas. L'indexation des salaires sur les prix disparaît sur 2003-2019 (période d'inflation basse) et
réapparaît avec 2022 : la boucle prix-salaires dépend du régime d'inflation, ce qu'une équation linéaire unique ne
représente pas.

## 8. Erreurs corrigées en version 0.6

Chaque correction est testée (tests/test_m14_identites.py, tests/validation_M8.py) ; la version 0.5 reste
reproductible (étiquette git `v0.5`).

1. **Effet du coût d'usage du capital cumulé chaque année** (m8_modele.py). L'effet de long terme d'une variation du
   coût d'usage (IS, taux d'intérêt) était appliqué au niveau de l'investissement de l'année précédente, qui le
   contenait déjà : il se cumulait (≈ 3,5 fois l'élasticité estimée à long terme). Sa montée en charge partait en outre
   de l'année de base (2022) et non de la mesure, d'où un effet presque complet dès 2028. Corrigé : effet appliqué en
   niveau, convergeant vers ε·Δln(coût d'usage) à la vitesse de rappel des branches. Baisse de l'IS de 25 % à 20 % :
   investissement +0,9 % en 2035 au lieu de +3 % ; PIB +0,07 % au lieu de +0,22 %. Concerne aussi tous les chocs de taux
   d'intérêt (rétroactions européennes, variantes de taux OAT).
2. **Double compte de l'investissement des ménages** (m8_modele.py, exogenes_observes). Depuis la v0.5 l'investissement
   en logement est endogène, mais l'indice exogène de la FBCF « autres » observé l'incluait encore : sa dynamique était
   comptée deux fois dans les rétrosimulations. Corrigé : l'indice exclut les ménages.
3. **Part des dividendes versée aux non-résidents** : 0,40 (référence CAC 40) ramenée à 0,30 (ensemble des sociétés,
   Banque de France), plage 0,20-0,50.
4. **Dispositif de sensibilité** : la première version modifiait les paramètres dès 2023 sans recalage ; la trajectoire
   de référence dérivait sur la période observée (élasticité de substitution à 0,3 : 34 millions d'emplois en 2024 au
   lieu de 30,6 ; 0,2 : divergence). Les paramètres alternatifs s'appliquent désormais à partir de 2026, et l'ancrage
   des termes de rappel neutralise les changements de niveau d'équilibre ; les paramètres calculés à l'initialisation
   (θ, élasticité au coût d'usage) passent par le même mécanisme. Les résultats de la première passe ont été écartés.
   Cette erreur d'outil aurait conduit à conclure, à tort, que l'élasticité de substitution est le paramètre dominant.
5. **Nouvel instrument de scénario** : marge de prix par branche (`Exogenes.marges_branche`), utilisé pour le choc
   d'énergie produite en France (test 6b) ; sans effet par défaut.
6. **Hypothèses de construction paramétrables** : réactions des hauts revenus (`hypotheses.comportements`) et
   élasticité du capital public (`hypotheses.elasticite_capital_public`) ; sans effet par défaut.

**Effet des corrections sur les variantes de l'audit v0.5** (modèle complet, 2032, avant → après) :

| Variante | PIB v0.5 | v0.6 | FBCF v0.5 | v0.6 | Emploi v0.5 | v0.6 | Dette v0.5 | v0.6 |
|---|---|---|---|---|---|---|---|---|
| 1. Salaires +2 % (choc ponctuel 2028) | +0.00 % | +0.01 % | +0.11 % | +0.10 % | -40 | -39 | -2.91 | -2.92 |
| 2. IS de 25,8 % à 20 % | +0.22 % | +0.08 % | +2.39 % | +0.74 % | +49 | +18 | +2.17 | +2.55 |
| 3. Consommation publique +1 pt de PIB | +0.59 % | +0.59 % | +0.20 % | +0.18 % | +205 | +205 | -0.32 | -0.33 |
| 4a. Réindustrialisation −20 %, immédiate, sans coût (borne haute) | +0.23 % | +0.45 % | +0.64 % | +0.81 % | +6 | +34 | -7.28 | -7.70 |
| 4b. Réindustrialisation −20 % en 5 ans, investissement et surcoût 10 % | +0.72 % | +0.82 % | +2.68 % | +2.60 % | +119 | +129 | -1.53 | -1.66 |
| 5. Prix de l'énergie importée +50 % | -1.05 % | -1.04 % | -1.58 % | -1.51 % | -324 | -323 | +5.13 | +5.10 |

Seule la baisse d'IS change notablement (effet sur le PIB divisé par 2,75). La réindustrialisation immédiate gagne
0,2 point car le choc de taux d'intérêt induit (rétroactions) n'est plus amplifié. Jeux de mesures des candidats :
écarts de 0,08 point de PIB au plus (Glucksmann −0,30 → −0,22 % ; Mélenchon −1,02 → −0,98 %), solde et dette
quasiment inchangés.
Rétrosimulation 2015-2019 (base 2014) : erreur sur le PIB en 2019 −1,0 % (v0.5 : −0,2 %), sur l'investissement −4,9 %
(v0.5 : −0,4 %) ; la v0.5 devait une partie de sa précision à l'erreur sur le coût d'usage (forte baisse des taux en
2015-2019, effet cumulé). L'investissement en logement est sous-estimé de 5 % en 2019, l'investissement des entreprises
d'environ 18 Md€ : la reprise de l'investissement de 2017-2019 n'est pas expliquée par les mécanismes estimés.

## 9. Recommandations d'amélioration

| Rang | Amélioration | Importance | Incidence probable | Données | Coût | Priorité |
|---|---|---|---|---|---|---|
| 1 | Estimer ou encadrer la fermeture d'offre : règle de politique monétaire de la zone euro et conditions de crédit (taux des crédits nouveaux, Banque de France), écart de production | indispensable | très forte (premier facteur d'incertitude) | BCE, Banque de France (trimestrielles) | moyen | 1 |
| 2 | Offre de travail et âge de départ : élasticité de l'emploi des seniors, substituabilité entre générations, effets sur le chômage (littérature : Rabaté, DARES, COR) | indispensable | très forte pour les réformes des retraites | Insee, DARES, COR | moyen | 1 |
| 3 | Réestimer sur données trimestrielles (1990-2024) avec traitement des ruptures (2008, 2020-2021) : consommation, salaires, prix | indispensable | forte (paramètres instables, n = 23) | Insee (comptes trimestriels) | élevé | 2 |
| 4 | Boucle prix-salaires dépendant du régime d'inflation ; prix de l'énergie et marges par branche (prix de production Insee) | importante | forte sur la dette et 2022-2024 | Insee (IPP), Eurostat | moyen | 2 |
| 5 | Productivité du travail et rétention de main-d'œuvre (2022-2024) | importante | forte sur l'emploi | Insee, Banque de France | moyen | 2 |
| 6 | Revenus temporaires et permanents ; propensions par âge, patrimoine et dette (HFCS, enquête Patrimoine) | importante | moyenne (mesures ponctuelles, redistribution) | Insee, Banque de France (accès restreint pour les microdonnées) | moyen | 3 |
| 7 | Emploi peu qualifié et allègements de cotisations dégressifs ; secteurs exposés et abrités | importante | moyenne (SMIC, cotisations) | DARES, Insee | moyen | 3 |
| 8 | Taux de marge → investissement ; R&D ; rachats d'actions | secondaire | moyenne (IS) | Insee (comptes de secteurs) | faible | 3 |
| 9 | Contenu importé par produit et par quintile | secondaire | faible (≤ 2 points de VA domestique) | Insee, Eurostat | faible | 4 |
| 10 | Bilans et comptes financiers (cadre stock-flux) | secondaire pour les mesures budgétaires | forte pour les scénarios de taux et de dette | Banque de France | élevé | 4 |

Arbitrage de périmètre à expliciter (non technique) : la fermeture d'offre traduit une vision du fonctionnement de
l'économie à moyen terme (rôle de la demande ou de l'offre). Tant qu'elle n'est pas estimée, le simulateur devrait
présenter les résultats de fin de mandat sous au moins deux hypothèses de bouclage plutôt qu'une seule valeur.

## 10. Limites persistantes et ce que le modèle ne sait pas dire

Le modèle ne sait pas dire :
- si les programmes qui combinent une relance et une baisse de l'âge de départ (Glucksmann, Mélenchon) augmentent ou
  réduisent le PIB et l'emploi en fin de mandat ;
- l'effet des programmes sur le ratio de dette publique au-delà du signe de l'effet sur le solde ;
- l'effet d'une hausse ciblée sur les bas salaires sur l'emploi peu qualifié (équations agrégées) ;
- ce que deviennent les profits libérés par une baisse d'impôt (fourchette seulement) et l'effet d'une épargne
  placée à l'étranger ou en actifs existants (pas de bilans financiers) ;
- l'effet des mesures non chiffrées par les candidats et de celles qui ne relèvent pas de ses mécanismes (préférence
  nationale, blocage des prix, capitalisation, décote, règles constitutionnelles) ;
- les effets d'anticipation (2027) : les écarts commencent en 2028 par construction ;
- la probabilité d'un résultat : les plages de sensibilité ne sont pas des intervalles de probabilité ; seule
  l'incertitude d'estimation des coefficients a une interprétation statistique, et elle ne couvre ni la
  spécification ni les hypothèses.
Ce qu'il peut dire avec une confiance raisonnable : le sens de l'effet de chaque programme sur le solde public dans
cinq cas sur six, les effets de première année, l'ordre de grandeur des multiplicateurs de dépense et de recettes,
les effets de redistribution sur la consommation, et le sens des effets pour les programmes dont les plages ne
contiennent pas zéro.

## 11. Sources

- Banque de France : Bulletins 249/8 (2023), 255/5 (2024), 261/3 (2025) sur la détention des actions par les
  non-résidents ; projections macroéconomiques (septembre 2026).
- Insee : Focus n° 338 (2024) ; Note de conjoncture de juin 2019 ; Économie et Statistique n° 472-473 (Garbinti et
  Lamarche 2014 ; Arrondel, Lamarche et Savignac) ; n° 513 (épargne de précaution).
- Banque de France, document de travail n° 962 (Garbinti, Lamarche, Savignac 2024), hétérogénéité des patrimoines et
  propension à consommer la richesse.
- Morris M. (1991), « Factorial sampling plans for preliminary computational experiments », Technometrics ; Campolongo
  F., Cariboni J., Saltelli A. (2007), « An effective screening design for sensitivity analysis of large models »,
  Environmental Modelling & Software ; Saltelli A. et al. (2008), Global Sensitivity Analysis: The Primer.
- Jappelli T., Pistaferri L. (2014) ; Fagereng A., Holm M., Natvik G. (2021) ; Kaplan G., Violante G. (2014),
  « A model of the consumption response to fiscal stimulus payments », Econometrica.
- Cette G., Lecat R., Ly-Marin C. (2016), « Long-term growth and productivity projections in advanced countries »
  (élasticité de substitution) ; Bom P., Ligthart J. (2014).
- France Stratégie, Comité d'évaluation des réformes de la fiscalité du capital (2019-2023).
- Eurostat, comptes nationaux annuels et comptes de secteurs ; tableaux entrées-sorties 2022.
