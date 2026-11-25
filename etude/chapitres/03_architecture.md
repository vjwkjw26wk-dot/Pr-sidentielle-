# Architecture scientifique du modèle {#sec:architecture}

Ce chapitre décrit l'organisation du modèle : ses modules, la manière dont ils s'articulent, le déroulement d'une
simulation annuelle, l'articulation avec la microsimulation, le traitement du calendrier des mesures, les régimes de
politique économique, la démographie et les retraites, et la cohérence comptable entre secteurs. Les équations sont
détaillées au chapitre \ref{sec:equations}.

## Vue d'ensemble et modules {#sec:modules}

Le modèle est écrit en Python ; il est organisé en modules numérotés (M1 à M27), conservés dans le dépôt du projet
avec leurs tests. Le tableau suivant en donne la liste fonctionnelle.

| Couche | Modules | Rôle |
|---|---|---|
| Données et comptes | M1 démographie, M3 cadre comptable, M5 tableau entrées-sorties et prix de Leontief | population par âge et sexe (projections Insee 2026), comptes des secteurs institutionnels, structure productive en 64 produits et 25 branches marchandes |
| Ménages (micro) | M4 population et OpenFisca, M10 couplage micro-macro, M14 hétérogénéité, M16 distribution dynamique | impôt sur le revenu et prestations ménage par ménage ; propensions à consommer par décile ; transitions emploi-chômage en espérance |
| Comportements | M7 équations estimées, M13 réponses des hauts revenus et patrimoines, M15 offre de travail, M9 activité des seniors et retraites | emploi, prix, salaires, consommation, investissement, logement, commerce ; élasticités fiscales ; participation ; départs à la retraite et pensions |
| Cœur | M8 (avec M17 dette par cohortes, M18 prix, M19 salaires, M21 compte des sociétés) | résolution annuelle, fermeture d'offre, finances publiques, comptes d'agents |
| Référence | M8_reference | trajectoire à politique inchangée : calage 2023-2025, prévisions du FMI 2026-2031, hypothèses de long terme |
| Europe et monnaie | M11 (zone euro), M24 politique monétaire et conditions financières | règle de la BCE, taux allemand, prime souveraine, taux des crédits |
| Incertitude, validation | M12, M22 | variantes de paramètres, validation prédictive (millésimes du FMI) |
| Régimes et programmes | M23 régimes, M25 traduction des programmes, M26 contraintes européennes, M27 corpus des programmes | moteur d'évaluation environnement × régime × programme |

La version de référence de cette étude est la configuration **P4** (section \ref{sec:gel}), qui ajoute à la version
0.9 une équation des prix de valeur ajoutée fondée sur une frontière des prix des facteurs et un compte complet des
sociétés non financières.

## Environnement, régime et programme {#sec:env-regime-prog}

Le principe d'organisation de l'évaluation distingue trois objets.

- **L'environnement** $E$ décrit l'économie à politique inchangée : les équations, leurs paramètres, et une
  trajectoire de référence calibrée de 2022 à 2047 (exogènes et termes de calage). Il est calibré une seule fois par
  configuration et par convention de dépense, puis mis en cache avec une empreinte de tous ses paramètres. Un
  environnement est modifié seulement si l'on change une équation ou un paramètre structurel qui exige un recalage
  (par exemple l'élasticité de substitution $\sigma$).
- **Le régime** $R$ décrit les règles de politique économique appliquées pendant la projection : règle budgétaire
  (aucune, stabilisation du ratio de dette, ajustement vers une cible ; effort figé ou réactif), régime monétaire (taux
  exogènes ou règle de la BCE, prime souveraine), jeu de paramètres fragiles (ancrage des anticipations, vitesse de
  fermeture), paramètres structurels modifiables sans recalage.
- **Le programme** $P$ est l'ensemble des mesures d'un candidat, traduites en modifications des exogènes du modèle
  (taux d'imposition, dépenses, prestations, règles de retraite, etc.), chacune avec sa date de première application.

L'effet d'un programme est défini comme

$$\text{Effet}(P \mid E, R) = Y(E, R, P) - Y(E, R, \varnothing),$$

où $Y$ désigne la trajectoire simulée. Dans le régime principal (« R2 figé »), l'effort budgétaire de la règle est
celui de la trajectoire sans programme : le programme ne déclenche pas d'effort supplémentaire, de sorte que son
effet n'est pas confondu avec la réaction de la règle. Dans les régimes « actifs », la règle réagit au programme
(chapitre \ref{sec:robustesse}).

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[node distance=1.2cm and 1.6cm, every node/.style={font=\small},
  boite/.style={draw, rounded corners, align=center, minimum width=3.2cm, minimum height=1cm, fill=gray!8},
  fleche/.style={-{Stealth[length=2.5mm]}, thick}]
\node[boite] (env) {\textbf{Environnement $E$}\\équations, paramètres,\\référence calibrée (cache)};
\node[boite, right=of env] (reg) {\textbf{Régime $R$}\\règle budgétaire, BCE,\\prime souveraine, jeux};
\node[boite, right=of reg] (prog) {\textbf{Programme $P$}\\mesures datées\\(corpus M27 → M25)};
\node[boite, below=1.6cm of reg, minimum width=5cm] (sim) {\textbf{Simulation annuelle M8}\\2023 → 2047};
\node[boite, below left=1.4cm and -0.6cm of sim] (yp) {$Y(E,R,P)$};
\node[boite, below right=1.4cm and -0.6cm of sim] (y0) {$Y(E,R,\varnothing)$};
\node[boite, below=3.4cm of sim, minimum width=5cm] (eff) {\textbf{Effet} $= Y(E,R,P) - Y(E,R,\varnothing)$};
\draw[fleche] (env) -- (sim); \draw[fleche] (reg) -- (sim); \draw[fleche] (prog) -- (sim);
\draw[fleche] (sim) -- (yp); \draw[fleche] (sim) -- (y0);
\draw[fleche] (yp) -- (eff); \draw[fleche] (y0) -- (eff);
\end{tikzpicture}
\caption{Organisation de l'évaluation : environnement, régime, programme.}
\end{figure}
```

## Fonctionnement d'une année de simulation {#sec:annee}

Chaque année $t$ de la projection est résolue par un **point fixe amorti** : on cherche des valeurs de la production,
des salaires et du chômage telles que toutes les équations de l'année soient satisfaites simultanément. L'algorithme
itère au plus 60 fois, avec un amortissement de 0,5 et un critère de convergence de $10^{-7}$. L'ordre des calculs dans
une itération est le suivant :

1. **Crochets de régime** (avant la résolution, avec l'information disponible jusqu'en $t-1$) : régime monétaire
   (taux directeur, taux allemand, écart souverain, taux des crédits), puis règle budgétaire (effort et répartition
   entre instruments), puis, le cas échéant, objectif budgétaire du candidat (lecture B) ;
2. **prix d'importation** (prix mondiaux, énergie) ;
3. **salaires, prix de la valeur ajoutée par branche, prix de Leontief** des produits et de la consommation ;
4. **emploi et investissement** par branche ;
5. **revenu disponible des ménages et demande finale** (consommation, logement, investissement, dépenses publiques,
   exportations) ;
6. **importations et production** par branche (système de Leontief).

Après convergence, le modèle calcule le PIB potentiel et l'écart de production, puis les comptes des administrations
publiques (recettes, dépenses, charge d'intérêts par cohortes, solde, dette) et le compte des sociétés (intérêts,
impôt sur les sociétés, dividendes, épargne, capacité de financement, dette). Ces comptes ne rétroagissent sur
l'année qu'à travers des variables retardées (dividendes de l'exercice précédent, dette de fin d'année précédente),
ce qui correspond au calendrier réel (les dividendes de l'année $t$ rémunèrent l'exercice $t-1$) et garantit qu'aucune
information future n'est utilisée.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[node distance=0.55cm, every node/.style={font=\small},
  etape/.style={draw, rounded corners, align=center, minimum width=9cm, minimum height=0.75cm, fill=blue!4},
  fleche/.style={-{Stealth[length=2.5mm]}, thick}]
\node[etape] (a) {Crochets de régime : BCE, taux, règle budgétaire, objectif (info. $\le t-1$)};
\node[etape, below=of a] (b) {Prix d'importation};
\node[etape, below=of b] (c) {Salaires $\to$ prix de VA $\to$ prix de Leontief};
\node[etape, below=of c] (d) {Emploi et investissement par branche};
\node[etape, below=of d] (e) {Revenu disponible $\to$ demande finale};
\node[etape, below=of e] (f) {Importations $\to$ production (Leontief)};
\node[etape, below=0.9cm of f, fill=green!6] (g) {Potentiel, finances publiques, compte des sociétés, comptes d'agents};
\draw[fleche] (a)--(b); \draw[fleche] (b)--(c); \draw[fleche] (c)--(d); \draw[fleche] (d)--(e); \draw[fleche] (e)--(f);
\draw[fleche] (f.east) -- ++(1.0,0) |- node[pos=0.25, right, align=left]{point fixe\\(≤ 60 itérations)} (c.east);
\draw[fleche] (f)--(g);
\end{tikzpicture}
\caption{Déroulement d'une année de simulation.}
\end{figure}
```

## La fermeture d'offre : comment la demande rejoint le potentiel {#sec:fermeture}

Un modèle dont la production est déterminée par la demande ne revient pas nécessairement à son potentiel : rien dans
les équations de court terme ne garantit que le chômage revienne à son niveau structurel. Les modèles institutionnels
résolvent ce problème par des mécanismes de retour (effet des prix sur la demande réelle, réaction de la politique
monétaire, effets de richesse). Dans le modèle de l'étude, ces canaux sont soit absents (pas de taux de change propre,
pas d'effets de richesse), soit faibles ; une **fermeture explicite** les représente : un supplément de demande
résorbe chaque année une fraction $\rho = 0{,}2$ de l'écart de production [B, inféré de la durée des écarts de
production 1982-2019], et anticipe une part $\theta = 0{,}75$ des révisions du potentiel [C]. Cette fermeture est
l'hypothèse qui gouverne la transition du court au long terme : avec $\rho = 0{,}1$, les effets de demande durent
deux fois plus longtemps ; avec $\rho = 0{,}3$, ils s'estompent plus vite. Les deux variantes, et une fermeture
pilotée par le chômage, font partie des régimes de robustesse.

## Microsimulation et articulation avec OpenFisca {#sec:micro}

Les mesures qui modifient l'impôt sur le revenu, la CSG ou les prestations sous condition de ressources sont évaluées
sur une **population de ménages** construite par le module M4 à partir du recensement de 2022 (fichier détail des
individus) et des tableaux fiscaux de la DGFiP (impôt sur le revenu par tranche, déclarations nationales). L'impôt est
calculé par OpenFisca-France (moteur public de la législation) sur un échantillon de 2 % des ménages ; les
prestations (RSA, prime d'activité, allocations familiales, aides au logement) sur deux sous-échantillons de 0,5 %, avec
un taux de recours apparent mesuré en législation actuelle (RSA 0,68, prime d'activité 0,66).

Le **couplage micro-macro** (M10) fonctionne dans un seul sens :

1. la réforme est décrite par des paramètres OpenFisca modifiés ;
2. l'impôt et les prestations sont calculés ménage par ménage en législation actuelle et après réforme (effet
   statique, comportements inchangés, revenus de 2024) ;
3. les écarts sont ramenés aux montants versés (foyers DGFiP, taux de recours) et répartis par décile de niveau de
   vie ;
4. les montants agrégés (M€ de 2024) entrent dans le modèle bouclé, indexés sur le PIB nominal simulé ; des
   propensions marginales à consommer par décile (M14) traduisent la répartition en effet sur la consommation.

Ce couplage a deux limites assumées : les revenus de la microsimulation ne sont pas revalorisés avec les salaires,
l'emploi et les prix simulés (pas de retour macro → micro), et les comportements des ménages ne sont pas
microsimulés (l'offre de travail passe par des élasticités moyennes, M15). Les mesures sur les revenus du capital et
les patrimoines (prélèvement forfaitaire unique, impôt sur la fortune, successions) sont évaluées sur des assiettes
agrégées, avec une répartition approchée sur le haut de la distribution.

**Risque de double compte.** Une mesure ne doit pas être comptée à la fois par la microsimulation et par un canal
agrégé. Le pont des programmes (M25) le garantit : les montants statiques de la microsimulation remplacent les
montants des canaux agrégés correspondants ; les profits induits par les mesures passent par le compte des sociétés
(M21), et non plus par une hypothèse séparée de M14 (double compte supprimé en phase 4.3). Le chapitre
\ref{sec:donnees} présente les contrôles correspondants.

## Traitement des dates de lancement des mesures {#sec:dates}

Chaque mesure porte une **première année d'application**. Par défaut, il s'agit de 2028, premier budget voté après
l'élection de 2027 ; le corpus retient 2027 lorsque le candidat annonce une application dès l'année de l'élection
(collectif budgétaire de l'été 2027, ordonnances de juillet 2027) et des dates ultérieures lorsqu'il l'annonce (par
exemple la réforme des retraites du RN au 1er janvier 2028). Le pont des programmes accepte des **listes de mesures
datées**, de sorte que deux mesures de même nature peuvent avoir des calendriers différents. Une application au
cours de l'année est approchée par l'année entière suivante ou, si nécessaire, par un prorata (non utilisé dans les
résultats de base). Le pas annuel a été conservé après examen : les mesures des programmes sont annuelles et les
horizons d'analyse sont de cinq ans et plus (chapitre \ref{sec:donnees}).

## Régimes budgétaires {#sec:regimes-budgetaires}

La règle budgétaire générique (M23) détermine chaque année un **effort** $e_t$ (en points de PIB), réparti entre
quatre instruments : consommation publique, prestations, impôts des ménages, impôts sur les produits (TVA). Sa forme
est

$$\bar s_t = \frac{\bar r - \bar g}{1 + \bar g}\,d_{t-1}, \qquad s^*_t = \bar s_t + \beta\,(d_{t-1} - d^*), \qquad
\Delta e_t = \text{clip}\left(\alpha\,(s^*_t - s^{ca}_{t-1}),\ 0,\ \bar e\right),$$

où $\bar s$ est le solde primaire stabilisant la dette, $\bar r$ et $\bar g$ les moyennes sur trois ans du taux
apparent et de la croissance nominale potentielle, $s^{ca}$ le solde primaire corrigé du cycle (semi-élasticité 0,5),
$d^*$ la cible de dette, $\alpha$ la vitesse d'ajustement et $\bar e$ le plafond annuel. Une clause de sauvegarde
suspend l'effort quand l'écart de production est inférieur à −1,5 point. Les régimes nommés sont : R0 (aucune règle),
R1 (stabilisation, $\beta = 0$), R2 (ajustement, $\alpha = 0{,}5$, $\beta = 0{,}02$, $d^* = 90\,\%$, plafond 0,5
point, répartition 30/20/30/20) [H, choix du projet], en mode figé ou actif, symétrique ou non.

**Lecture par objectifs budgétaires (lecture B).** Pour représenter la trajectoire de solde annoncée par un
candidat, un second dispositif s'ajoute à la règle du régime : chaque année, un effort supplémentaire
$\Delta e^B_t = \text{clip}\left(c_t - s_{t-1}, -2, 2\right)$ rapproche le solde effectif $s$ de la cible $c_t$
(interpolée linéairement entre les points annoncés, tenue ensuite), et se répartit selon la composition déduite des
déclarations du candidat. Trois passes de simulation corrigent la cible interne de l'écart réalisé, ce qui revient à
supposer que le gouvernement anticipe correctement la dérive du solde [H]. Le chapitre \ref{sec:resultats} présente
les écarts résiduels à la cible.

## Politique monétaire et réaction de la BCE {#sec:bce}

Dans le régime principal, les taux d'intérêt sont **exogènes** : le taux court de référence est l'Euribor à trois mois
observé (2,63 % en octobre 2026) et le taux long l'OAT à dix ans (dernière observation mensuelle), maintenus
constants. Ce choix isole l'effet propre des programmes ; il revient à supposer que la BCE ne réagit pas à un choc
français (la France pèse environ 20 % de la zone euro) et que la prime souveraine est inchangée.

Dans le **régime monétaire endogène** (M24), la BCE suit une règle de Taylor estimée en écart à la référence, sur
l'inflation et l'activité de la zone euro, auxquelles la France contribue selon son poids ; le taux allemand à dix ans
réagit au taux directeur ; l'écart entre l'OAT et le taux allemand dépend de la dette et du solde public français en
écart à la référence (prime souveraine estimée sur un panel de la zone euro hors 2010-2013, avec une variante incluant
la crise) ; les taux des crédits nouveaux aux ménages et aux sociétés s'ajustent partiellement aux taux de marché
(séries MIR de la BCE). Les taux des crédits entrent dans l'arbitrage consommation-épargne des ménages et dans le coût
d'usage du capital des entreprises.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[node distance=0.8cm and 1.3cm, every node/.style={font=\small},
  b/.style={draw, rounded corners, align=center, minimum width=2.8cm, minimum height=0.9cm, fill=orange!6},
  f/.style={-{Stealth[length=2.5mm]}, thick}]
\node[b] (fr) {Inflation, activité\\France ($t-1$)};
\node[b, right=of fr] (ze) {Inflation, activité\\zone euro};
\node[b, right=of ze] (bce) {Taux directeur\\(règle de Taylor)};
\node[b, below=of bce] (bund) {Taux allemand\\10 ans};
\node[b, below=of fr] (finpub) {Dette, solde\\France ($t-1$)};
\node[b, right=of finpub] (prime) {Écart souverain\\(prime)};
\node[b, below=of prime] (oat) {OAT 10 ans};
\node[b, below=of bund] (cred) {Taux des crédits\\ménages, sociétés};
\node[b, below=of oat] (dem) {Consommation,\\investissement, intérêts};
\draw[f] (fr) -- (ze); \draw[f] (ze) -- (bce); \draw[f] (bce) -- (bund);
\draw[f] (finpub) -- (prime); \draw[f] (prime) -- (oat); \draw[f] (bund) -- (oat);
\draw[f] (bce) -- (cred); \draw[f] (oat) -- (cred); \draw[f] (cred) -- (dem); \draw[f] (oat) -- (dem);
\end{tikzpicture}
\caption{Transmission monétaire et financière dans le régime endogène (M24).}
\end{figure}
```

## Conditions financières et prime souveraine {#sec:prime}

La prime souveraine (écart entre l'OAT et le taux allemand) est estimée sur un panel de pays de la zone euro avec
effets fixes : environ 1,3 point de base par point de dette publique (en % du PIB) et 1,5 point de base par point de
déficit, hors période de crise ; en incluant 2010-2013, l'effet du déficit est beaucoup plus fort (11,8 points de base
par point) [E]. Ces coefficients sont des moyennes historiques : ils ne disent rien des épisodes de crise de confiance,
qui sont non linéaires. Le module M26 permet donc d'ajouter des chocs d'écart (variante « tension »), dont l'ampleur
est une hypothèse de scénario.

## Contraintes européennes {#sec:contraintes-ue}

Le module M26 qualifie chaque mesure au regard du droit de l'Union (niveau 0 : compétence nationale ; 1 :
aménagement ; 2 : contentieux probable ; 3 : effet sur la trajectoire budgétaire et la procédure de déficit excessif ;
4 : incompatibilité avec les traités) et produit trois variantes : *conforme* (mesures mises en conformité, part non
conforme des mesures de niveau 4 retirée), *contentieux* (en plus, mesures de niveaux 1-2 reportées et partiellement
retirées) et *tension* (en plus, amendes de la procédure de déficit excessif et choc de prime souveraine). Le
chapitre \ref{sec:europe} les détaille.

## Démographie et retraites {#sec:demo-retraites}

La démographie (M1) reprend les projections de population de l'Insee (2026, scénario central) par âge et sexe. Le
module des retraites (M9) relie la population, les règles de retraite, l'activité des seniors, le nombre de retraités
et la masse des pensions :

- l'**activité des seniors** de 55 à 74 ans est modélisée par âge, sexe et génération, en fonction de l'écart entre
  l'âge et un **âge pivot** qui dépend de l'âge d'ouverture des droits (AOD) ; le profil est estimé sur les taux
  d'activité de l'enquête Emploi (Eurostat, 2003-2019) et testé hors échantillon sur 2020-2025 (relèvement de l'AOD
  de 62 ans à 62 ans et 9 mois) ;
- depuis la finalisation, l'âge pivot dépend aussi de la **durée d'assurance requise** : chaque année de durée
  supplémentaire reporte l'âge effectif de cessation d'activité de 9 mois pour les hommes et de 5 mois pour les femmes,
  d'après l'évaluation de la réforme de 1993 (Bozio, 2011) [E, littérature] ; et une fraction de chaque génération peut
  relever de **conditions particulières** (carrières longues à un âge donné, ou maintien des conditions actuelles) ;
- les **pensions** sont calculées par génération (salaire de référence, revalorisation sur les prix), calées sur la
  masse observée ; la durée requise modifie le niveau des pensions de la fraction des assurés qui ne reportent pas leur
  départ (proratisation et décote sur la part de base) [H] ;
- les **liens avec le modèle bouclé** passent par la population active, l'emploi des seniors supplémentaires (part
  estimée sur 2010-2019) et l'écart de masse des pensions.

La section \ref{sec:eq-retraites} donne les équations et le chapitre \ref{sec:distribution} les effets
générationnels.

## Distribution des revenus et effets sur les ménages {#sec:distrib-archi}

Trois niveaux de lecture distributive coexistent : (i) l'effet **statique** des mesures socio-fiscales par décile de
niveau de vie (microsimulation) ; (ii) l'effet **macroéconomique moyen** sur le pouvoir d'achat, les salaires, l'emploi
et les prix ; (iii) un module de **distribution dynamique** simplifié (M16), qui répartit les variations d'emploi, de
salaires et de transferts entre ménages en espérance. Seuls (i) et (ii) sont utilisés dans les résultats de cette
étude ; (iii) est mentionné comme piste.

## Relations entre secteurs institutionnels {#sec:secteurs}

Le modèle tient les comptes de quatre secteurs : ménages (S14-S15), sociétés non financières (S11, compte complet
depuis la phase 4.3 ; les sociétés financières sont traitées de manière agrégée), administrations publiques (S13) et
reste du monde (S2). Les flux principaux sont représentés sur la figure suivante.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[every node/.style={font=\scriptsize},
  s/.style={draw, rounded corners, align=center, minimum width=3.0cm, minimum height=1.0cm, fill=gray!10, font=\small},
  f/.style={-{Stealth[length=2.2mm]}, thick}]
\node[s] (men) at (-5.2,0) {\textbf{Ménages}};
\node[s] (snf) at (5.2,0) {\textbf{Sociétés}};
\node[s] (apu) at (0,4.2) {\textbf{Administrations}\\\textbf{publiques}};
\node[s] (rdm) at (0,-4.2) {\textbf{Reste du monde}};
\draw[f] (snf.165) -- node[above]{salaires, dividendes, intérêts} (men.15);
\draw[f] (men.345) -- node[below]{consommation, logement} (snf.195);
\draw[f] (men.70) to[bend left=12] node[above left, align=right]{impôts, cotisations,\\TVA} (apu.180);
\draw[f] (apu.210) to[bend left=12] node[below right, align=left, pos=0.55]{prestations,\\salaires publics} (men.45);
\draw[f] (snf.110) to[bend right=12] node[above right, align=left]{IS, impôts de production,\\cotisations} (apu.0);
\draw[f] (apu.330) to[bend right=12] node[below left, align=right, pos=0.55]{commande publique,\\subventions} (snf.135);
\draw[f] (snf.250) to[bend left=12] node[below right, align=left]{importations,\\dividendes versés} (rdm.0);
\draw[f] (rdm.30) to[bend left=12] node[above left, align=right, pos=0.45]{exportations} (snf.225);
\draw[f] (apu.270) -- node[right, pos=0.35]{intérêts versés aux non-résidents} (rdm.90);
\end{tikzpicture}
\caption{Principaux flux entre secteurs institutionnels représentés dans le modèle.}
\end{figure}
```

**Conventions comptables.** Les identités suivantes sont vérifiées à chaque simulation : la somme des capacités de
financement des secteurs est nulle (aux erreurs de calage près, explicitées) ; le revenu national brut est égal au PIB
plus les revenus primaires nets reçus du reste du monde ; la variation de la dette publique est égale au besoin de
financement (hors ajustements stock-flux observés jusqu'en 2025) ; les prix de Leontief vérifient l'égalité entre
coûts et prix pour chaque produit. Le chapitre \ref{sec:donnees} présente les résultats de ces contrôles.

**Risques de double comptabilisation identifiés et traités.**

| Risque | Traitement |
|---|---|
| Une mesure fiscale comptée par la microsimulation et par un canal agrégé | les montants microsimulés remplacent le canal agrégé (M25) |
| Profits induits par une mesure comptés deux fois (M14 et compte des sociétés) | supprimé en phase 4.3 : seul le compte des sociétés répartit les profits |
| Investissement hors budget (pôle public bancaire) compté en dépense publique | mesure `investissement_hors_apu` : effet de demande sans coût pour le solde public ; distincte de l'investissement public |
| Composantes d'une enveloppe comptées en plus de l'enveloppe (RN : collectivités et agences dans la « réorganisation de l'État ») | composantes non additionnées (corpus) |
| Effort de la lecture B superposé à une mesure du programme | l'effort B est calculé sur le solde résultant des mesures : il ne couvre que l'écart restant |
| Amendes européennes comptées comme dépense intérieure | comptées en dépense publique sans effet de demande (transfert à l'Union) |
| Coût des retraites compté dans M9 et dans une ligne de transferts | les réformes de retraite passent par M9 seulement ; les revalorisations de pensions annoncées séparément passent par les transferts |
