# Introduction générale et problématique {#sec:intro}

## Le contexte économique et budgétaire français à l'automne 2026 {#sec:contexte}

L'élection présidentielle d'avril-mai 2027 s'ouvre dans une configuration macroéconomique que la France n'avait
pas connue depuis la création de l'euro : un déficit public durablement supérieur à 5 % du produit intérieur brut
(PIB), une dette publique qui dépasse 115 % du PIB et continue de croître, une charge d'intérêts qui a doublé en
quelques années sous l'effet de la remontée des taux, une croissance faible (de l'ordre de 1 % par an ou moins), un
taux de chômage remonté au-dessus de 7 % et une procédure européenne pour déficit excessif ouverte depuis 2024. Les
chiffres de référence utilisés dans cette étude sont ceux des comptes nationaux publiés par l'Insee et Eurostat
jusqu'en 2025, prolongés par la trajectoire « à politique inchangée » décrite au chapitre \ref{sec:architecture} :
déficit de 5,1 % du PIB en 2025, dette de 115,7 %, chômage de 7,4 %, taux de l'obligation assimilable du Trésor
(OAT) à dix ans de 4,89 % en octobre 2026 (dernier point mensuel disponible, Eurostat) contre 3,82 % en moyenne sur
douze mois.

Trois éléments de ce contexte conditionnent toute évaluation de programme.

1. **L'effet « boule de neige »** de la dette. Lorsque le taux d'intérêt apparent de la dette publique devient
   supérieur au taux de croissance nominal du PIB, le ratio d'endettement augmente mécaniquement, même avec un
   solde primaire (hors intérêts) à l'équilibre. Cette condition, presque oubliée pendant la décennie de taux très
   bas (2012-2021), est redevenue d'actualité. Elle signifie que l'horizon long des simulations est dominé par la
   dynamique de la dette et par l'hypothèse de taux, beaucoup plus que par le contenu des programmes.
2. **Le vieillissement**. Les générations nombreuses de l'après-guerre sont à la retraite ; la masse des pensions de
   droit direct représente de l'ordre de 13 à 14 % du PIB, et le rapport entre cotisants et retraités continue de
   diminuer. Les trois candidats étudiés proposent des réformes des retraites de sens opposés (retour à 62 ans, voire
   60 ans, d'un côté ; 65 ans et 45 annuités de l'autre), ce qui en fait l'un des terrains de comparaison les plus
   nets.
3. **La contrainte européenne**. La France est soumise au cadre budgétaire réformé en 2024 (trajectoire de dépenses
   nettes, procédure de déficit excessif), à la politique monétaire unique de la Banque centrale européenne (BCE) et
   au droit de l'Union (TVA, aides d'État, politique commerciale, libre circulation des capitaux). Plusieurs mesures
   des programmes se heurtent à ce cadre ; leur faisabilité et leur calendrier en dépendent (chapitre
   \ref{sec:europe}).

## Problématique : comparer rigoureusement des programmes différents {#sec:problematique}

La question centrale de l'étude est la suivante :

> **Comment comparer rigoureusement les conséquences économiques et sociales de programmes présidentiels qui
> diffèrent par leur philosophie, leurs instruments, leur calendrier et la précision de leur chiffrage ?**

Elle se décompose en trois difficultés.

**Hétérogénéité des instruments.** Un programme combine des dizaines de mesures : impôts, prestations, dépenses
publiques, règles du marché du travail, retraites, normes, politique commerciale. Leurs effets passent par des
canaux différents (demande, offre, prix, incitations, finances publiques) et à des horizons différents. Les comparer
exige un cadre commun où chaque mesure est traduite dans les mêmes variables.

**Hétérogénéité de la documentation.** Les programmes ne sont pas chiffrés avec la même précision. À la date de
l'étude (novembre 2026), La France insoumise (LFI) a publié un « budget rectificatif » pour 2027 détaillant 106,4
milliards d'euros (Md€) de recettes et 81,7 Md€ de dépenses nouvelles ; le Rassemblement national (RN) a présenté
une enveloppe de 140 Md€ d'économies nettes d'ici 2032, partiellement ventilée ; Horizons (Édouard Philippe) annonce
près de 150 Md€ d'économies et un déficit sous 2,5 % du PIB en fin de quinquennat, avec peu de mesures chiffrées une
à une. Une comparaison honnête ne doit pas donner artificiellement le même niveau de précision à des programmes dont
le chiffrage diffère. C'est pourquoi l'étude propose, pour chaque candidat, **deux lectures** : une lecture « par
mesures documentées » (lecture A) et une lecture « par objectifs budgétaires » (lecture B), qui reconstruit l'effort
nécessaire pour atteindre la trajectoire de solde annoncée (chapitre \ref{sec:resultats}).

**Incertitude des mécanismes.** Les effets macroéconomiques d'une mesure dépendent de paramètres mal connus
(multiplicateurs, élasticités, réactions des marchés et de la BCE, anticipations) et de choix de modélisation sur
lesquels les économistes ne s'accordent pas (chapitre \ref{sec:theorie}). Une comparaison crédible doit montrer ce
qui résiste à ces incertitudes et ce qui en dépend.

## Pourquoi les chiffrages statiques ne suffisent pas {#sec:statique}

Le débat public s'appuie surtout sur des **chiffrages statiques** : le coût d'une mesure est calculé en multipliant
une assiette par un taux, à comportements et à activité inchangés. Ces chiffrages sont indispensables (ils sont le
point de départ de tout le reste) mais ils ne répondent pas à la question posée, pour quatre raisons.

1. **Les comportements réagissent.** Une hausse de l'imposition des revenus du capital réduit l'assiette (les
   dividendes distribués diminuent, certains contribuables optimisent ou partent) ; une baisse de TVA n'est que
   partiellement répercutée sur les prix ; un allongement de la durée d'assurance ne se traduit que partiellement
   par des départs plus tardifs. Le rendement « net » d'une mesure peut être très inférieur à son rendement statique
   (section \ref{sec:incidence}).
2. **L'activité réagit.** Une dépense publique supplémentaire augmente la demande, donc la production, les
   revenus et les recettes fiscales ; une économie budgétaire produit l'effet inverse. Le coût budgétaire final d'une
   mesure diffère de son coût direct d'un montant qui dépend du multiplicateur et de l'élasticité des recettes à
   l'activité (encadré ci-dessous).
3. **Les prix et les taux réagissent.** Les hausses de salaires se diffusent aux prix ; les déficits peuvent faire
   monter la prime de risque souveraine ; la BCE réagit à l'inflation et à l'activité de la zone euro.
4. **Le temps compte.** Les effets de demande sont rapides, les effets d'offre (capital, productivité, participation
   au marché du travail) sont lents ; une mesure peut être favorable à cinq ans et défavorable à vingt, ou l'inverse.

> **Encadré 1.1 — Coût budgétaire direct et effet macroéconomique final : un exemple chiffré.**
> Considérons une baisse de 10 Md€ de la consommation publique, dans une économie où le PIB vaut 3 000 Md€, où le
> multiplicateur de court terme est $m$ et où les recettes publiques représentent $\tau = 52\,\%$ du PIB. L'économie
> directe est de 10 Md€ (0,33 point de PIB). Le PIB diminue de $m \times 10$ Md€ ; les recettes diminuent de
> $\tau \times m \times 10$ Md€. Le gain budgétaire net est donc $10 \times (1 - \tau m)$ Md€ : 4,8 Md€ si $m = 1$,
> 2,8 Md€ si $m = 1{,}4$. Quant au ratio de dette $d = D/Y$, il varie de
> $\Delta d \approx (-\Delta D)/Y - d \cdot \Delta Y / Y$ : la baisse du dénominateur peut l'emporter sur la baisse du
> numérateur. Avec $d = 1{,}2$, la consolidation **augmente** le ratio de dette la première année dès que
> $m > 1/(d + \tau) \approx 0{,}58$. Le modèle utilisé ici a un multiplicateur de consommation publique d'environ
> 1,2 la première année (section \ref{sec:multiplicateurs}) : une consolidation par la dépense dégrade le ratio de dette
> pendant plusieurs années avant de l'améliorer. Ce n'est pas un paradoxe du modèle, c'est une propriété
> arithmétique bien documentée (Blanchard et Leigh, 2013 ; FMI, 2010).

## L'intérêt d'une approche dynamique, macroéconomique et microéconomique {#sec:approche}

Pour dépasser le chiffrage statique, l'étude s'appuie sur un modèle macroéconométrique de la France construit pour ce
projet, à partir de données ouvertes uniquement, et couplé à une microsimulation des ménages. Ses principes :

- **Macroéconomie bouclée.** Les comptes de tous les secteurs (ménages, sociétés non financières, administrations
  publiques, reste du monde) sont tenus de manière cohérente ; un revenu versé par l'un est reçu par l'autre ; les
  identités comptables sont vérifiées à chaque simulation (chapitre \ref{sec:donnees}).
- **Multisectoriel.** La production est décrite par 25 branches marchandes reliées par le tableau des entrées-sorties
  (TES) de l'Insee, ce qui permet de suivre la diffusion des prix et des contenus en importations.
- **Microéconomie des ménages.** Les mesures fiscales et sociales sont évaluées ménage par ménage sur un échantillon
  représentatif construit à partir du recensement et des données fiscales, avec le moteur de calcul public
  OpenFisca-France ; leurs effets distributifs sont mesurés par décile de niveau de vie (chapitre
  \ref{sec:distribution}).
- **Régimes de politique économique explicites.** La règle budgétaire suivie après le programme, la réaction de la
  BCE, la formation des taux souverains et les réactions institutionnelles européennes sont des choix de scénario,
  documentés et variables, et non des hypothèses cachées.

L'architecture distingue trois objets (chapitre \ref{sec:architecture}) : l'**environnement** (l'économie à politique
inchangée, calibrée une fois), le **régime** (les règles de politique budgétaire et monétaire), et le **programme**
(les mesures du candidat). L'effet d'un programme est toujours mesuré comme la différence entre deux simulations dans
le même environnement et sous le même régime, l'une avec et l'autre sans le programme.

## Les candidats retenus {#sec:candidats}

L'étude porte sur trois candidats représentatifs de trois philosophies économiques distinctes :

- **Jean-Luc Mélenchon** (La France insoumise), dont le programme *L'Avenir en commun* (5\textsuperscript{e} édition, novembre 2026,
  1 069 mesures) privilégie la relance par les revenus des ménages modestes et la dépense publique, financée par une
  hausse de l'imposition du capital et des hauts patrimoines ;
- **Marine Le Pen** (Rassemblement national), dont le programme combine des baisses ciblées d'impôts (TVA sur
  l'énergie, jeunes, familles), un retour partiel sur la réforme des retraites et des économies concentrées sur
  l'immigration, la contribution européenne et l'organisation de l'État ;
- **Édouard Philippe** (Horizons), retenu comme candidat du centre, dont le programme privilégie la réduction des
  dépenses publiques (près de 150 Md€), l'allongement de la vie active (65 ans, 45 annuités), la réduction de 250 000
  postes de fonctionnaires et un « pacte » de baisse des impôts de production financée par la baisse des aides aux
  entreprises.

**Justification du choix du candidat du centre.** À la date du corpus (24 novembre 2026), le programme d'Édouard
Philippe est le seul programme du centre et du centre droit publié sous une forme structurée (quinze thèmes sur son
site, un « volume 1 » de 142 mesures présenté le 18 novembre 2026, un volet de finances publiques avec un objectif
chiffré). Pour Gabriel Attal, les sources consultées ne donnaient qu'une enveloppe d'économies (120 à 150 Md€ selon
les sources). Ce choix sera réévalué lorsque d'autres programmes seront suffisamment détaillés ; le corpus et le code
permettent d'ajouter un candidat sans modification du modèle (annexe \ref{sec:annexe-j}).

Le choix de trois candidats ne préjuge ni de leur poids électoral ni d'un jugement sur les autres programmes ; il
vise à couvrir la diversité des philosophies économiques présentes dans le débat.

## Questions de recherche, hypothèses et périmètre {#sec:questions}

L'étude cherche à répondre aux questions suivantes.

- **Q1.** Quels sont les effets macroéconomiques (activité, emploi, prix, revenus, finances publiques) de chaque
  programme, mesure par mesure et dans son ensemble, à 5 et 10 ans, et sous quelles hypothèses à 20 ans ?
- **Q2.** Quelle part de ces effets est robuste aux incertitudes de modélisation (paramètres, régimes, environnement,
  réactions européennes) ?
- **Q3.** Quels mécanismes de transmission expliquent les écarts entre programmes ?
- **Q4.** Qui gagne et qui perd, au moins au premier ordre, parmi les ménages (déciles, actifs et retraités,
  générations) ?
- **Q5.** Quelles mesures se heurtent aux contraintes européennes, et avec quelles conséquences possibles ?

Hypothèses de travail : les programmes sont pris tels qu'ils sont publiés, sans les compléter par des intentions
supposées ; lorsqu'une traduction dans le modèle exige une hypothèse (par exemple la composition d'une enveloppe
d'économies), cette hypothèse est explicitée, marquée [H] et accompagnée de variantes. Les hypothèses de traduction
retenues par l'auteur du modèle ne sont jamais présentées comme des engagements des candidats.

Périmètre : économie française, horizon 2027-2046, pas annuel. Hors périmètre : modélisation complète de l'économie
européenne et mondiale, effets environnementaux (émissions), effets sur la qualité des services publics, effets
politiques et sociaux non économiques.

> **Avertissement méthodologique.** Les simulations présentées dans cet ouvrage sont des **scénarios
> conditionnels** : elles répondent à la question « que se passerait-il, selon ce modèle et sous ces hypothèses, si
> ce programme était appliqué tel qu'il est décrit ? ». Ce ne sont pas des prévisions. Elles ne disent pas ce qui va
> se passer, ni ce qu'un gouvernement ferait effectivement, ni comment évolueraient les chocs extérieurs. Leur
> valeur tient à la cohérence comptable, à la transparence des hypothèses et à l'analyse de sensibilité, non à une
> précision qu'aucun modèle ne possède.

## Plan de l'étude {#sec:plan}

Le chapitre \ref{sec:theorie} présente les fondements théoriques et les désaccords entre écoles qui justifient — ou
contestent — les équations du modèle. Les chapitres \ref{sec:architecture} à \ref{sec:donnees} décrivent le modèle :
architecture, équations, données, estimations et validation. Le chapitre \ref{sec:programmes} présente en détail les
trois programmes et leur traduction. Le chapitre \ref{sec:transmission} explique la transmission macroéconomique des
grandes familles de mesures, et le chapitre \ref{sec:europe} les contraintes européennes. Le chapitre
\ref{sec:resultats} présente les résultats des simulations comparatives, le chapitre \ref{sec:distribution} leurs
effets distributifs, le chapitre \ref{sec:comportements} les limites des hypothèses comportementales, et le chapitre
\ref{sec:robustesse} la robustesse et les incertitudes. Le chapitre \ref{sec:discussion} compare les philosophies
économiques des programmes et le chapitre \ref{sec:conclusion} conclut. Les annexes (A à K) rassemblent les
registres, les équations complètes, les résultats détaillés, les tests, le glossaire et le guide de reproduction.

**Conventions de lecture.** Tout au long de l'ouvrage, les statuts suivants sont utilisés : **[D]** donnée observée
ou règle publiée ; **[E]** paramètre estimé par le projet ; **[C]** paramètre calibré sur la littérature ou sur une
cible ; **[H]** hypothèse de modélisation ou de scénario ; **[X]** exploratoire. Les effets sont exprimés en écart à
la trajectoire de référence (même environnement, même régime, sans le programme) : en pourcentage pour les volumes et
les prix, en points pour les taux (chômage, solde public, dette rapportés au PIB), en milliers pour l'emploi. Les
horizons « 5 ans », « 10 ans » et « 20 ans » désignent les années 2031, 2036 et 2046 (le programme commence en
2027).
