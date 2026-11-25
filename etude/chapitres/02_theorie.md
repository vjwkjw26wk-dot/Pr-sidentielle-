# Fondements théoriques de l'économie modélisée {#sec:theorie}

Un modèle macroéconométrique n'est pas une théorie unique : c'est un assemblage d'équations dont chacune résume un
mécanisme, et dont la forme reflète des choix théoriques. Ce chapitre présente les grandes écoles de pensée qui
justifient — ou contestent — ces choix. Pour chacune, on expose les intuitions, les mécanismes, les équations
fondamentales, les principaux résultats empiriques, les controverses, et ce que le modèle de l'étude en reprend, en
simplifie ou en écarte. L'objectif est double : permettre au lecteur de comprendre pourquoi le modèle produit les
résultats qu'il produit, et lui donner les moyens de juger ce qui changerait sous d'autres hypothèses.

Un fil conducteur traverse tout le chapitre : **la question de savoir si, et pendant combien de temps, la demande
détermine la production**. Les écoles qui répondent « longtemps » (keynésiennes, post-keynésiennes) attribuent de
grands effets aux politiques budgétaires ; celles qui répondent « peu ou pas » (classiques, nouvelle macroéconomie
classique) attribuent l'essentiel aux conditions de l'offre. Les modèles institutionnels contemporains, dont celui
de l'étude, adoptent une position intermédiaire : la demande compte à court terme, l'offre à long terme, et la
vitesse du passage de l'un à l'autre est l'un des paramètres les plus incertains et les plus influents.

## L'économie classique et néoclassique {#sec:classique}

**Intuitions.** Pour les économistes classiques (Smith, Ricardo, Say, puis Walras et Marshall pour la tradition
néoclassique), les prix flexibles ajustent l'offre et la demande sur chaque marché. Sur le marché du travail, le
salaire réel s'ajuste jusqu'à ce que toute personne souhaitant travailler au salaire courant trouve un emploi ; le
chômage durable ne peut être que volontaire ou dû à des rigidités (salaire minimum, syndicats, réglementations). Sur
le marché des biens, la production est déterminée par les facteurs disponibles (travail, capital) et la technologie :
c'est la « loi de Say », selon laquelle l'offre crée sa propre demande, car tout revenu versé est dépensé, consommé ou
épargné, et l'épargne finance l'investissement par l'intermédiaire du taux d'intérêt.

**Mécanismes et équations.** La production est donnée par une fonction de production

$$Y = F(K, AL),$$

où $Y$ est la production, $K$ le capital, $L$ le travail et $A$ l'efficience du travail (la technologie). Les
entreprises embauchent jusqu'à ce que la productivité marginale du travail égale le salaire réel,
$F_L(K, AL) = W/P$, et investissent jusqu'à ce que la productivité marginale du capital égale le coût réel du capital.
Sur le marché des fonds prêtables, le taux d'intérêt réel $r$ égalise l'épargne $S(r)$ et l'investissement $I(r)$.
Une hausse de la dépense publique financée par emprunt réduit l'épargne nationale, fait monter $r$ et évince
l'investissement privé d'un montant égal : le multiplicateur budgétaire est nul (« éviction totale »). La monnaie est
neutre : la théorie quantitative $MV = PY$ implique qu'une hausse de la masse monétaire $M$ se traduit par une hausse
proportionnelle des prix $P$.

**Résultats empiriques.** À long terme, plusieurs prédictions classiques sont bien vérifiées : la neutralité de la
monnaie sur l'activité réelle, le rôle dominant de la productivité dans la croissance du niveau de vie, l'ajustement
des salaires réels à la productivité. À court terme, elles le sont beaucoup moins : les récessions s'accompagnent de
hausses massives du chômage involontaire, que les prix et salaires ne résorbent que lentement.

**Controverses.** La critique keynésienne porte sur la flexibilité des prix et sur le lien entre épargne et
investissement : si les salaires nominaux baissent, la demande des salariés baisse aussi, et la déflation peut
aggraver le chômage en alourdissant les dettes (Fisher, 1933). La critique de la loi de Say porte sur la possibilité
de thésauriser : un revenu épargné sous forme de monnaie n'est pas dépensé.

**Ce que le modèle reprend.** Le cadre classique gouverne le **long terme** du modèle : la production tend vers un
PIB potentiel déterminé par la fonction de production (CES, section \ref{sec:eq-production}), la population active et
le chômage structurel ; la monnaie n'y a pas d'effet réel durable. Ce que le modèle écarte : l'ajustement instantané
des prix et l'éviction totale à court terme.

## La théorie keynésienne et le multiplicateur budgétaire {#sec:keynes}

**Intuitions.** Keynes (1936) part d'un constat : pendant la Grande Dépression, le chômage massif persiste alors que
les salaires baissent. Son explication tient en une idée : **la production est déterminée par la demande effective**.
Les entreprises produisent ce qu'elles anticipent de vendre ; si les ménages et les entreprises réduisent leurs
dépenses (par précaution, pessimisme, contrainte de crédit), la production et l'emploi baissent, ce qui réduit les
revenus, donc la dépense, dans un enchaînement cumulatif. Rien ne garantit que l'économie revienne spontanément au
plein emploi, car les salaires et les prix sont rigides à la baisse et parce qu'une baisse des salaires réduit aussi
la demande.

**Le multiplicateur.** Dans le modèle le plus simple, la consommation dépend du revenu disponible,
$C = c_0 + c\,(Y - T)$, où $c$ est la propension marginale à consommer. L'équilibre $Y = C + I + G$ donne

$$Y = \frac{c_0 - cT + I + G}{1 - c}, \qquad \frac{\partial Y}{\partial G} = \frac{1}{1-c}.$$

Avec $c = 0{,}6$, un euro de dépense publique supplémentaire produit 2,5 euros de PIB. En économie ouverte, une part
$\mu$ de la dépense est importée et une part $\tau$ du revenu est prélevée : le multiplicateur devient
$1/[1 - c(1-\tau) + \mu]$, soit environ 1,1 avec $c = 0{,}6$, $\tau = 0{,}45$ et $\mu = 0{,}3$. Le multiplicateur d'une
baisse d'impôt est plus faible que celui d'une dépense ($c$ fois plus faible au premier tour), car une partie du
revenu supplémentaire est épargnée.

**Le modèle IS-LM.** Hicks (1937) formalise Keynes en deux courbes : la courbe IS (équilibre du marché des biens,
production décroissante avec le taux d'intérêt, qui réduit l'investissement) et la courbe LM (équilibre du marché
monétaire, taux croissant avec la production pour une offre de monnaie donnée). Une relance budgétaire déplace IS ;
l'éviction passe par la hausse du taux d'intérêt, partielle si LM n'est pas verticale. Lorsque le taux est bloqué à
sa borne inférieure (« trappe à liquidité ») ou que la banque centrale le maintient fixe, l'éviction disparaît et le
multiplicateur est maximal.

**Résultats empiriques.** L'estimation des multiplicateurs est l'un des terrains les plus travaillés de la
macroéconomie empirique. Trois grandes familles d'approches existent :

- les **vecteurs autorégressifs structurels** (VAR) identifiant les chocs budgétaires par le délai de décision
  (Blanchard et Perotti, 2002) trouvent des multiplicateurs de dépense proches de 1 aux États-Unis ;
- les approches **narratives** (chocs de dépenses militaires, Ramey, 2011 ; chocs fiscaux, Romer et Romer, 2010)
  trouvent des multiplicateurs de dépense entre 0,6 et 1,2 et des effets d'impôt plus élevés ;
- les études **conditionnelles à l'état de l'économie** (Auerbach et Gorodnichenko, 2012) trouvent des
  multiplicateurs plus élevés en récession (supérieurs à 1,5) qu'en expansion (proches de 0,5), un résultat discuté
  (Ramey et Zubairy, 2018).

La revue de Ramey (2019) situe la plupart des estimations du multiplicateur de dépense entre 0,6 et 1. L'erreur de
prévision des organisations internationales pendant la crise de la zone euro (Blanchard et Leigh, 2013) a montré que
les multiplicateurs implicites de la consolidation de 2010-2012 avaient été sous-estimés (supérieurs à 1 au lieu de
0,5), ce qui a joué un rôle important dans la réévaluation de l'austérité.

**Controverses.** La critique monétariste et classique porte sur l'éviction et les anticipations (sections
\ref{sec:monetarisme} et \ref{sec:anticipations}) ; la critique « ricardienne » (Barro, 1974) soutient que des ménages
prévoyants épargnent la baisse d'impôt financée par la dette en prévision des impôts futurs. À l'opposé, la thèse de
« l'austérité expansionniste » (Giavazzi et Pagano, 1990 ; Alesina et Ardagna, 2010) soutenait qu'une consolidation
crédible pouvait stimuler l'activité par la confiance ; les travaux ultérieurs du FMI (Guajardo, Leigh et Pescatori,
2014) ont montré que ce résultat tenait largement à l'identification des épisodes et que les consolidations sont en
moyenne récessives à court terme.

**Ce que le modèle reprend.** Le cœur de court terme du modèle est keynésien : la production résulte de la demande
(consommation, investissement, dépenses publiques, exportations nettes des importations), elle-même fonction des
revenus. Les multiplicateurs du modèle (section \ref{sec:multiplicateurs}) se situent dans le haut de la fourchette
empirique pour la consommation publique (environ 1,2 la première année, 0,75 à cinq ans, avec un taux d'intérêt exogène), parce
que le modèle n'a pas d'effet d'éviction par le taux dans son régime principal et que la fermeture vers le potentiel
est lente. Ce point est central pour l'interprétation : sous le régime avec réaction de la BCE et prime de risque, ou
avec une fermeture plus rapide, les multiplicateurs sont plus faibles (chapitre \ref{sec:robustesse}).

## Synthèse néoclassique et nouvelle économie keynésienne {#sec:nouvelle-keynesienne}

**Intuitions.** La « synthèse néoclassique » (Samuelson, Modigliani, Tobin) réconcilie Keynes et les classiques :
keynésienne à court terme parce que les prix sont rigides, classique à long terme quand ils s'ajustent. La
**nouvelle économie keynésienne** (années 1980-2000) donne des fondements microéconomiques à cette rigidité : coûts
de changement des prix (« coûts de menu »), contrats échelonnés (Taylor, 1980 ; Calvo, 1983), concurrence
monopolistique, salaires d'efficience, rigidités réelles.

**Équations fondamentales.** Le modèle canonique (Clarida, Galí et Gertler, 1999 ; Woodford, 2003 ; Galí, 2015)
tient en trois équations log-linéarisées :

$$\tilde y_t = \mathbb{E}_t \tilde y_{t+1} - \frac{1}{\sigma}\left(i_t - \mathbb{E}_t \pi_{t+1} - r^n_t\right) \quad\text{(IS dynamique)}$$
$$\pi_t = \beta\,\mathbb{E}_t \pi_{t+1} + \kappa\,\tilde y_t \quad\text{(courbe de Phillips nouvelle keynésienne)}$$
$$i_t = \rho + \phi_\pi \pi_t + \phi_y \tilde y_t \quad\text{(règle de Taylor)}$$

où $\tilde y$ est l'écart de production, $\pi$ l'inflation, $i$ le taux nominal, $r^n$ le taux d'intérêt naturel. La
courbe de Phillips relie l'inflation aux tensions sur les capacités de production ; la règle de Taylor (1993) décrit
une banque centrale qui relève son taux plus que l'inflation ($\phi_\pi > 1$), stabilisant l'économie.

**Résultats empiriques.** Les modèles DSGE (dynamiques, stochastiques, d'équilibre général) de cette famille
(Smets et Wouters, 2007) sont devenus l'outil standard des banques centrales. Ils reproduisent correctement les
corrélations conjoncturelles, mais ont mal anticipé la crise financière de 2008 (absence de secteur financier) et la
faiblesse de l'inflation de la décennie 2010. La pente de la courbe de Phillips estimée sur données récentes est
faible (courbe « plate »), ce qui signifie que de fortes variations de chômage modifient peu l'inflation — jusqu'à
l'épisode inflationniste de 2021-2023, dont l'interprétation (chocs d'offre et non-linéarités) reste débattue.

**Controverses.** Les critiques portent sur les anticipations rationnelles (section \ref{sec:anticipations}), sur
l'agent représentatif (section \ref{sec:heterogenes}), et sur les effets de « guidage prospectif » irréalistes
(l'« énigme du guidage prospectif » : une promesse de taux bas dans dix ans a, dans ces modèles, un effet aujourd'hui
plus fort qu'une baisse immédiate).

**Ce que le modèle reprend.** Le modèle de l'étude n'est pas un DSGE : il appartient à la famille des modèles
macroéconométriques institutionnels (comme Mésange, de l'Insee et de la DG Trésor, ou FR-BDF de la Banque de France
pour son bloc d'équations de comportement), dont les équations sont estimées en correction d'erreur. Il reprend de la
nouvelle synthèse : la rigidité des prix et des salaires (ajustements partiels vers des cibles de long terme), une
courbe de Phillips sur les salaires (faible, calibrée) et une pente des prix à l'écart de production, et une règle de
Taylor pour la BCE dans le régime monétaire endogène (section \ref{sec:eq-monetaire}). Il écarte les anticipations
rationnelles généralisées (sauf en option pour le taux allemand).

## Le monétarisme et le rôle de la politique monétaire {#sec:monetarisme}

**Intuitions.** Friedman (1968) et Phelps (1967) affirment qu'il n'existe pas d'arbitrage durable entre inflation et
chômage : si la banque centrale cherche à maintenir le chômage sous son niveau « naturel », l'inflation accélère, car
les salariés intègrent l'inflation passée dans leurs revendications. La politique monétaire a des effets réels à
court terme, mais avec des délais « longs et variables » ; elle devrait suivre une règle simple plutôt que chercher à
piloter finement la conjoncture.

**Équations.** La courbe de Phillips augmentée des anticipations s'écrit

$$\pi_t = \pi^e_t - \alpha\,(u_t - u^*),$$

où $u^*$ est le chômage d'équilibre (NAIRU, *non-accelerating inflation rate of unemployment*). Avec des
anticipations adaptatives, $\pi^e_t = \pi_{t-1}$, maintenir $u_t < u^*$ entraîne une inflation qui accélère.

**Résultats empiriques.** La stagflation des années 1970 a validé l'essentiel du diagnostic de Friedman et Phelps et
conduit à l'indépendance des banques centrales et au ciblage d'inflation. Le lien quantitatif entre monnaie et
inflation s'est en revanche distendu à court terme (instabilité de la demande de monnaie), d'où l'abandon du ciblage
d'agrégats monétaires au profit des règles de taux.

**Controverses.** Le niveau de $u^*$ est incertain et varie dans le temps ; les estimations françaises vont de 7 à 9 %
selon les méthodes et les périodes. Les hystérèses (Blanchard et Summers, 1986) suggèrent qu'un chômage élevé
durablement peut augmenter $u^*$ lui-même.

**Ce que le modèle reprend.** Le chômage structurel $u^*$ est une hypothèse de la référence (7,5 % puis 7,0 %,
cohérente avec les hypothèses du FMI et du Conseil d'orientation des retraites) [C] ; il peut être modifié par
certaines mesures (assurance chômage, formation) ; la courbe de Phillips sur les salaires est faible. Dans la zone
euro, la politique monétaire est commune : la BCE réagit à l'inflation et à l'activité **de la zone**, dans lesquelles
la France pèse environ un cinquième ; une relance française n'appelle donc qu'une faible réaction de taux (section
\ref{sec:eq-monetaire}).

## Théorie de l'offre, fiscalité et incitations {#sec:offre}

**Intuitions.** L'économie de l'offre met l'accent sur les effets incitatifs des prélèvements : un impôt modifie les
prix relatifs (entre travail et loisir, entre consommation présente et future, entre investissement en France et à
l'étranger) et donc les comportements. Le coût d'un impôt pour l'économie dépasse la recette qu'il rapporte : c'est la
« charge excédentaire » (ou perte sèche), proportionnelle, en première approximation, au carré du taux et à
l'élasticité de l'assiette.

**Équations.** L'élasticité du revenu imposable au taux net d'impôt, $e = \frac{\partial \ln z}{\partial \ln(1-\tau)}$,
résume les réactions (heures, effort, optimisation, évasion). Saez, Slemrod et Giertz (2012) montrent que le taux
marginal qui maximise la recette sur les hauts revenus vaut

$$\tau^* = \frac{1}{1 + a\,e},$$

où $a$ est le paramètre de Pareto de la distribution des hauts revenus (environ 1,5 à 2). Avec $e = 0{,}25$ et $a = 2$,
$\tau^* \approx 67\,\%$ ; avec $e = 0{,}5$, $\tau^* = 50\,\%$. La « courbe de Laffer » est l'illustration générale de
cette relation entre taux et recette.

**Résultats empiriques.** Les élasticités sont faibles pour les heures travaillées des salariés à temps plein, plus
élevées pour la participation des femmes mariées et des seniors (marge extensive) et pour les très hauts revenus
(par l'optimisation et la requalification des revenus plutôt que par l'effort). Pour la France, les estimations sur
réformes (Cabannes, Houdré et Landais, 2014) trouvent des élasticités du revenu imposable de l'ordre de 0,1 à 0,2 pour
l'ensemble et plus élevées en haut de la distribution. Pour l'impôt sur les sociétés, les effets sur
l'investissement passent par le coût du capital (section \ref{sec:investissement}) ; l'incidence sur les salaires a
été estimée à environ la moitié pour l'impôt local allemand sur les entreprises (Fuest, Peichl et Siegloch, 2018).
Pour la TVA, l'incidence est asymétrique : les hausses sont répercutées plus que les baisses (Benzarti et al., 2020).

**Controverses.** Les élasticités de court terme (optimisation, décalage temporel des revenus) surestiment souvent
les effets de long terme ; la mobilité internationale des hauts patrimoines est discutée (les départs liés à
l'ancien impôt de solidarité sur la fortune sont estimés faibles en nombre mais concentrés en patrimoine). Les
promesses d'autofinancement des baisses d'impôt sont rarement vérifiées aux taux observés dans les pays de l'OCDE.

**Ce que le modèle reprend.** Le module M13 applique aux mesures sur les hauts revenus et les patrimoines des
élasticités issues de la littérature, avec des fourchettes basse, centrale et haute (revenu imposable 0,1-0,2-0,4 ;
capital 0,2-0,5-1,0 ; pertes d'assiette de l'impôt sur la fortune de 25 % puis 35 % à cinq ans en valeur centrale)
[C]. Le module M15 traduit les réformes des prestations en effets sur la participation au marché du travail [B].
L'incidence des prélèvements sur les entreprises (impôt sur les sociétés, impôts de production, cotisations) est
répartie entre prix, salaires et marges selon des parts calibrées (chapitre \ref{sec:transmission}).

## Théories de la croissance exogène et endogène {#sec:croissance}

**Intuitions.** Le modèle de Solow (1956) explique la croissance de long terme par l'accumulation du capital et le
progrès technique. Le capital ayant des rendements décroissants, l'accumulation seule ne suffit pas : à long terme,
le niveau de vie croît au rythme du progrès technique, supposé exogène. Les théories de la croissance endogène
(Romer, 1990 ; Lucas, 1988 ; Aghion et Howitt, 1992) rendent ce progrès dépendant de choix économiques : recherche et
développement, capital humain, concurrence, diffusion des connaissances. Les politiques publiques (éducation,
recherche, infrastructures) peuvent alors modifier le **taux** de croissance et pas seulement le niveau du PIB.

**Équations.** Dans le modèle de Solow, $\dot k = s\,f(k) - (n + g + \delta)\,k$, où $k$ est le capital par unité de
travail efficace, $s$ le taux d'épargne, $n$ la croissance démographique, $g$ le progrès technique et $\delta$ la
dépréciation. À l'état stationnaire, le PIB par tête croît au taux $g$. La comptabilité de la croissance décompose
$\Delta \ln Y = \alpha\,\Delta \ln K + (1-\alpha)\,\Delta \ln L + \Delta \ln \text{PGF}$, la productivité globale des
facteurs (PGF) étant le résidu.

**Résultats empiriques.** La convergence conditionnelle entre pays est confirmée (Mankiw, Romer et Weil, 1992). Les
rendements de la R&D sont élevés et largement sociaux (Hall, Mairesse et Mohnen, 2010) ; l'élasticité de la
production au capital public est estimée autour de 0,08 en moyenne (Bom et Ligthart, 2014). Le ralentissement de la
productivité dans les pays avancés depuis le milieu des années 2000 reste mal expliqué.

**Controverses.** L'ampleur des effets de long terme des politiques publiques sur la croissance est très incertaine ;
les effets de la fiscalité sur la croissance de long terme sont discutés (effets de niveau plutôt que de taux dans la
plupart des estimations).

**Ce que le modèle reprend.** La croissance de long terme du modèle est **exogène** : la productivité tendancielle
de chaque branche est un paramètre (dérivé des huit dernières années observées). Deux canaux endogènes exploratoires
existent : l'investissement public accroît le capital public, qui augmente la productivité avec une élasticité de
0,08 [C] ; l'aide à la R&D augmente le stock de R&D (élasticité 0,08, statut exploratoire) [X]. Les effets de
l'éducation, de la qualité des services publics et des réformes structurelles sur la productivité ne sont pas
représentés : c'est une limite qui pénalise les programmes dont les effets attendus passent par ces canaux (chapitre
\ref{sec:comportements}).

## Marché du travail, chômage structurel et loi d'Okun {#sec:travail}

**Intuitions.** Le chômage résulte de plusieurs causes : insuffisance de la demande (chômage keynésien), coût du
travail trop élevé par rapport à la productivité (chômage classique), frictions d'appariement entre offres et
demandes d'emploi (chômage frictionnel), inadéquation des qualifications. Les théories modernes (Mortensen et
Pissarides, 1994) décrivent le marché du travail comme un processus de recherche : le chômage d'équilibre dépend des
flux de créations et de destructions d'emplois, de l'efficacité de l'appariement et des conditions de négociation
salariale (dont l'assurance chômage, qui augmente le salaire de réserve).

**Équations.** La loi d'Okun (1962) relie les variations du chômage à l'écart de croissance :

$$\Delta u_t \approx -\beta_O\,(g_t - g^*) \quad\text{ou}\quad u_t - u^* \approx -\frac{1}{\beta_O'}\,\tilde y_t,$$

avec pour la France un coefficient de l'ordre de 0,3 à 0,5 point de chômage par point d'écart de production. La
courbe de Beveridge relie le taux d'emplois vacants au chômage. Dans les modèles de négociation, le salaire
d'équilibre augmente avec la productivité, l'indemnisation du chômage et le pouvoir de négociation, et diminue avec le
taux de chômage.

**Résultats empiriques.** La relation d'Okun est robuste en direction mais instable en coefficient. Les effets de
l'assurance chômage sur la durée du chômage sont bien établis (une indemnisation plus généreuse ou plus longue
allonge les épisodes), mais leurs effets agrégés sur le chômage d'équilibre sont plus incertains ; pour la France, Le
Barbanchon, Rathelot et Roulet (2019) trouvent un effet faible de la générosité sur le salaire de réserve. Les
allègements de cotisations sur les bas salaires ont des effets sur l'emploi peu qualifié documentés, plus faibles et
plus incertains au-delà de 1,6 SMIC.

**Controverses.** Le débat oppose ceux qui voient dans le chômage européen surtout un problème d'institutions (coût
du travail, protection de l'emploi, générosité des allocations) et ceux qui y voient surtout un problème de demande
persistante et d'hystérèse.

**Ce que le modèle reprend.** L'emploi de chaque branche marchande est déterminé par une demande de travail à
production donnée (CES, élasticité de substitution capital-travail $\sigma$) ; le chômage est la différence entre la
population active (démographie, retraites, offre de travail) et l'emploi. Le chômage structurel est exogène sauf pour
l'assurance chômage (0,063 point par 10 % d'allocations, fourchette 0-0,13) [B] et la formation [X]. Les salaires
suivent les prix avec une indexation partielle, la productivité et une courbe de Phillips faible. Un point de
vigilance, documenté au chapitre \ref{sec:robustesse} : dans certains chocs, l'écart de chômage du modèle réagit plus
fortement que ne l'implique la loi d'Okun, parce que l'emploi s'ajuste à la production branche par branche alors que
la population active est en partie exogène.

## Théories de la consommation et de l'épargne {#sec:consommation}

**Intuitions.** Keynes faisait dépendre la consommation du revenu courant. Friedman (1957, revenu permanent) et
Modigliani et Brumberg (1954, cycle de vie) la font dépendre des ressources de toute la vie : un ménage lisse sa
consommation, épargne pendant la vie active et désépargne à la retraite ; un revenu transitoire est surtout épargné,
un revenu permanent surtout consommé. Ces théories impliquent des propensions marginales à consommer faibles pour les
transferts temporaires — sauf si les ménages sont contraints dans leur accès au crédit.

**Équations.** Avec un taux d'intérêt égal au taux de préférence pour le présent, l'hypothèse du revenu permanent
donne $C_t = \frac{r}{1+r}\left[A_t + \sum_{k \ge 0} \frac{\mathbb{E}_t Y_{t+k}}{(1+r)^k}\right]$ : la consommation
réagit aux révisions du revenu permanent, pas aux variations anticipées. L'équation d'Euler,
$u'(C_t) = \beta(1+r)\,\mathbb{E}_t u'(C_{t+1})$, relie la croissance de la consommation au taux réel avec une
élasticité de substitution intertemporelle (EIS) dont la méta-analyse de Havranek (2015) situe la valeur centrale
autour de 0,3 à 0,5 une fois corrigé le biais de publication.

**Résultats empiriques.** Les propensions marginales à consommer observées sont beaucoup plus élevées que ne le
prédit l'hypothèse du revenu permanent pure, surtout pour les ménages modestes ou peu liquides (Jappelli et
Pistaferri, 2010) ; l'épargne de précaution (Carroll, 1997) et les contraintes de liquidité (Deaton, 1991) expliquent
cet écart. Les ménages réagissent aux chocs permanents de revenu bien plus qu'aux chocs transitoires (Blundell,
Pistaferri et Preston, 2008). Pendant la crise sanitaire, l'épargne forcée a montré la sensibilité de la consommation
à l'incertitude.

**Controverses.** L'importance relative des ménages « non ricardiens » (qui consomment leur revenu courant) varie
selon les études et les périodes ; l'effet de la dette publique sur l'épargne des ménages (équivalence ricardienne)
est jugé faible empiriquement, mais non nul.

**Ce que le modèle reprend.** La consommation agrégée suit une équation à correction d'erreur estimée sur le revenu
disponible réel (élasticité de long terme unitaire), complétée par une épargne de précaution (0,3 % de consommation par
point de chômage, fourchette 0,1-0,6) et un effet du taux réel du crédit à l'habitat (0,2, fourchette 0-0,5) [C].
Pour les mesures socio-fiscales, des propensions marginales à consommer par décile (module M14) font que les
transferts aux ménages modestes stimulent davantage la consommation que les baisses d'impôt pour les ménages aisés.
L'équivalence ricardienne est écartée.

## Théories de l'investissement et du coût du capital {#sec:investissement}

**Intuitions.** Trois familles d'explications coexistent. Le **principe d'accélérateur** fait dépendre
l'investissement de la croissance anticipée de la demande. La théorie **néoclassique** (Jorgenson, 1963 ; Hall et
Jorgenson, 1967) le fait dépendre du coût d'usage du capital, qui combine taux d'intérêt, dépréciation, fiscalité et
prix relatif des biens d'équipement. La théorie du **q de Tobin** (1969) le fait dépendre du rapport entre la valeur
de marché des entreprises et le coût de remplacement de leur capital. S'y ajoutent les contraintes financières
(l'autofinancement compte quand l'accès au crédit est imparfait) et l'incertitude (option d'attendre, Bloom, 2009).

**Équations.** Le coût d'usage s'écrit, en notation simplifiée,

$$c_K = \frac{p_I}{p}\,\frac{(r + \delta)(1 - z\,\tau)}{1 - \tau},$$

où $p_I/p$ est le prix relatif de l'investissement, $r$ le taux d'intérêt réel, $\delta$ la dépréciation, $\tau$ le
taux de l'impôt sur les sociétés et $z$ la valeur actualisée des amortissements fiscaux. Le capital désiré
$K^* = \alpha Y / c_K$ (production Cobb-Douglas) ou $K^* \propto Y\,c_K^{-\sigma}$ (CES).

**Résultats empiriques.** L'accélérateur est l'explication la plus robuste à court terme ; l'élasticité de
l'investissement au coût du capital est significative mais modeste à moyen terme, de l'ordre de −0,5 à −1 selon les
études microéconomiques récentes. L'effet du CICE sur l'investissement a été jugé faible par les évaluations de
France Stratégie ; la trésorerie supplémentaire a été surtout utilisée pour les marges et le désendettement.

**Ce que le modèle reprend.** L'investissement de chaque branche suit un accélérateur en correction d'erreur [E],
avec un coût d'usage qui intègre l'impôt sur les sociétés et, depuis la phase 5, le taux des crédits aux sociétés
non financières transmis par le bloc monétaire [E]. Un canal de trésorerie (0,10 de l'épargne supplémentaire des
entreprises investie, fourchette 0-0,3) [C] relie profits et investissement. Les effets de l'incertitude politique
sur l'investissement ne sont pas représentés (chapitre \ref{sec:comportements}).

## Anticipations rationnelles, adaptatives et contraintes de liquidité {#sec:anticipations}

**Intuitions.** La façon dont les agents forment leurs anticipations change radicalement l'effet des politiques. Avec
des **anticipations adaptatives**, les agents extrapolent le passé ; une politique nouvelle les surprend et produit des
effets tant qu'ils ne l'ont pas apprise. Avec des **anticipations rationnelles** (Muth, 1961 ; Lucas, 1972 ; Sargent
et Wallace, 1975), les agents connaissent le modèle et utilisent toute l'information disponible : une politique
annoncée et crédible est intégrée immédiatement, et seules les surprises ont des effets réels (proposition
d'inefficacité de Sargent et Wallace).

**La critique de Lucas.** Lucas (1976) montre que les paramètres des équations estimées (propension à consommer,
réaction des salaires) dépendent eux-mêmes de la politique en vigueur ; un modèle estimé sous un régime ne permet donc
pas, en toute rigueur, de prévoir les effets d'un changement de régime. C'est une critique directe des modèles
macroéconométriques du type de celui de l'étude.

**Contraintes de liquidité.** Même des agents parfaitement rationnels ne peuvent lisser leur consommation s'ils ne
peuvent emprunter ; une part significative des ménages se comporte donc « à la Keynes ». Les modèles modernes
combinent anticipations rationnelles et hétérogénéité des contraintes (section \ref{sec:heterogenes}).

**Résultats empiriques.** Les enquêtes d'anticipations (inflation, revenus) montrent des anticipations ni
parfaitement rationnelles ni purement adaptatives : elles sont hétérogènes, réagissent avec retard, et dépendent de
l'expérience vécue. Les marchés financiers, en revanche, intègrent rapidement l'information sur les politiques
monétaires annoncées.

**Ce que le modèle reprend.** Les anticipations sont adaptatives (implicites dans les dynamiques de correction
d'erreur), avec une option d'anticipations rationnelles pour la transmission du taux directeur au taux allemand à
dix ans. La critique de Lucas s'applique : les résultats doivent être lus comme les effets d'une politique dans un
environnement dont les comportements restent ceux observés de 1997 à 2019, ce qui est d'autant moins vrai que la
politique est éloignée de l'expérience historique (chapitre \ref{sec:comportements}). Les **effets de crédibilité**
(une règle d'or constitutionnelle qui réduirait la prime de risque, une politique jugée insoutenable qui
l'augmenterait) ne sont représentés que par la prime souveraine et les variantes de tension.

## Économie ouverte, commerce international et compétitivité {#sec:ouverte}

**Intuitions.** Dans une économie ouverte, une partie de la demande intérieure est satisfaite par des importations
(fuite du multiplicateur), et la demande étrangère soutient la production nationale par les exportations. La
compétitivité dépend des prix relatifs (coûts salariaux, productivité, change) et de facteurs hors prix (qualité,
spécialisation, innovation). Le modèle de Mundell-Fleming (1962-1963) montre qu'en changes fixes et mobilité des
capitaux, la politique budgétaire est efficace et la politique monétaire nationale inopérante — la situation d'un
pays de la zone euro vis-à-vis de ses partenaires.

**Équations.** Les exportations en volume dépendent de la demande mondiale adressée et de la compétitivité-prix,
$\ln X = \ln D^* - \eta_X \ln (p_X / p^*)$ ; les importations dépendent de la demande pondérée par les contenus en
importations et des prix relatifs, $\ln M = \ln D - \eta_M \ln(p_M / p)$. La condition de Marshall-Lerner donne les
conditions sous lesquelles une dépréciation améliore le solde commercial.

**Résultats empiriques.** Les élasticités-prix du commerce sont modestes à court terme et plus élevées à long terme ;
la compétitivité hors prix explique une part importante de la dégradation des parts de marché françaises depuis
2000. Les droits de douane sont en grande partie supportés par les acheteurs du pays importateur (épisode américain
de 2018-2019) et appellent des représailles.

**Controverses.** La pertinence des politiques de relocalisation et de protection, l'ampleur des gains de
l'intégration commerciale et leur répartition (« choc chinois », Autor, Dorn et Hanson, 2013) restent discutées.

**Ce que le modèle reprend.** Exportations et importations suivent des équations estimées [E] ; le TES permet de
suivre les contenus en importations de chaque composante de la demande. Les droits de douane (curseur hors
programme) sont modélisés de manière stylisée (part hors UE des importations, répercussion, riposte), en rappelant
qu'ils relèvent de la compétence européenne. Il n'y a pas de taux de change propre à la France.

## Économie institutionnelle et contraintes budgétaires {#sec:institutions}

**Intuitions.** Les institutions — règles budgétaires, indépendance de la banque centrale, droit européen,
organisation de la protection sociale — encadrent les politiques possibles et influencent les anticipations. North
(1990) en fait des « règles du jeu » qui déterminent la performance économique de long terme. En matière budgétaire,
deux questions dominent : la soutenabilité de la dette et l'interaction entre politiques budgétaire et monétaire.

**Équations.** La dynamique du ratio de dette $d$ s'écrit

$$d_t = \frac{1 + i_t}{1 + g_t}\,d_{t-1} - s_t,$$

où $i$ est le taux d'intérêt apparent, $g$ la croissance nominale et $s$ le solde primaire (en % du PIB). Le solde
primaire qui stabilise le ratio est $s^* = \frac{i - g}{1 + g}\,d$. Bohn (1998) propose un critère de soutenabilité :
la dette est soutenable si le solde primaire réagit positivement au ratio de dette. Leeper (1991) distingue les
régimes où la politique budgétaire est « passive » (elle stabilise la dette) de ceux où elle est « active » (la
politique monétaire doit alors s'adapter, ou l'inflation ajuste la valeur réelle de la dette).

**Résultats empiriques.** Le seuil de dette au-delà duquel la croissance serait durablement plus faible, avancé par
Reinhart et Rogoff (2010), n'a pas résisté à la vérification (erreurs de calcul relevées par Herndon, Ash et Pollin,
2014) ; il n'existe pas de seuil universel. Blanchard (2019) a souligné qu'avec des taux inférieurs à la croissance,
le coût budgétaire de la dette était faible ; la remontée des taux depuis 2022 a inversé cette situation pour la
France. Les primes de risque souveraines réagissent à la dette et aux déficits, de manière non linéaire et
fortement dépendante du contexte (crise de la zone euro de 2010-2012).

**Ce que le modèle reprend.** Le module M23 représente les règles budgétaires (stabilisation du ratio de dette,
ajustement vers une cible, clause de sauvegarde) ; M24 représente la réaction de la BCE et la prime souveraine
estimée sur un panel de la zone euro ; M26 représente le cadre européen (procédure de déficit excessif, droit de la
TVA, compétences de l'Union). La dynamique de la dette est calculée par cohortes d'émission (M17).

## Approches stock-flux cohérentes et modèles à agents hétérogènes {#sec:heterogenes}

**Approches stock-flux cohérentes.** Héritières de Tobin et développées par Godley et Lavoie (2007), elles imposent
que chaque flux financier ait une contrepartie et que les stocks (dettes, actifs) résultent de l'accumulation des
flux. Elles attirent l'attention sur les déséquilibres de bilans (endettement privé, position extérieure) que les
modèles centrés sur les flux ignorent, et sur l'interdépendance des soldes sectoriels : le solde public, le solde
privé et le solde extérieur somment à zéro.

**Modèles à agents hétérogènes.** Les modèles HANK (*Heterogeneous Agent New Keynesian*, Kaplan, Moll et Violante,
2018) remplacent l'agent représentatif par une distribution de ménages différant par leurs revenus, leur patrimoine et
leur accès au crédit. Ils montrent que la transmission de la politique monétaire passe surtout par les effets de
revenu indirects (emploi, salaires) plutôt que par la substitution intertemporelle, et que les effets des politiques
budgétaires dépendent de qui reçoit les transferts et de qui paie les impôts.

**Ce que le modèle reprend.** Le modèle tient les comptes de tous les secteurs institutionnels et vérifie les
identités entre flux (capacités et besoins de financement) à chaque simulation ; il suit la dette publique par
cohortes et la dette des sociétés non financières. Il n'a pas de bilan complet des ménages ni de position extérieure
détaillée. L'hétérogénéité des ménages est représentée de manière « semi-structurelle » : la microsimulation calcule
l'effet de chaque mesure ménage par ménage, et des propensions à consommer par décile traduisent cet effet en demande.
Ce n'est pas un modèle HANK : les comportements individuels ne sont pas optimisés et la distribution ne réagit pas
dynamiquement à la conjoncture (sauf dans le module de distribution dynamique M16, simplifié).

## Synthèse : ce que les désaccords théoriques changent pour l'évaluation des programmes {#sec:synthese-theorie}

Le tableau suivant résume, pour les grandes familles de mesures des programmes, le sens des effets selon les écoles,
et la position du modèle.

| Famille de mesures | Lecture keynésienne | Lecture classique / offre | Position du modèle (régime principal) |
|---|---|---|---|
| Hausse de dépense publique | effet positif fort à court terme (multiplicateur > 1 en sous-emploi) | éviction, effet faible ; hausse future des impôts | multiplicateur ≈ 1,2 à 1 an, 0,75 à 5 ans ; éviction par les taux seulement en régime BCE + prime |
| Hausse des transferts aux ménages modestes | effet positif (propension à consommer élevée) | effet désincitatif possible sur le travail | effet de demande selon les propensions par décile ; effet sur la participation pour les prestations sous condition de ressources (M15) |
| Hausse des impôts sur le capital et les patrimoines | effet de demande faible (propension faible des hauts revenus) | réduction de l'épargne, de l'investissement, départs | érosion d'assiette (M13) ; effet de demande faible ; pas d'effet sur l'investissement par le patrimoine |
| Baisse des impôts de production, des cotisations | effet de demande modéré | baisse du coût, compétitivité, emploi | baisse des prix (répercussion 50 %), hausse des marges et des salaires selon l'incidence |
| Réforme des retraites (âge) | relèvement : baisse de revenu des seniors, chômage | hausse de l'offre de travail et du potentiel | M9 : population active, pensions ; la fermeture absorbe progressivement l'offre supplémentaire |
| Consolidation budgétaire | récessive, peut dégrader le ratio de dette à court terme | confiance, baisse des taux | récessive ; amélioration du ratio de dette à moyen terme seulement ; prime souveraine en option |

Ces écarts ne se résolvent pas par une meilleure estimation d'un seul paramètre : ils tiennent à la vitesse à
laquelle l'économie revient vers son potentiel, à la réaction des taux et aux anticipations. C'est pourquoi l'étude
présente systématiquement ses résultats sous plusieurs régimes (règle budgétaire, politique monétaire, vitesse de
fermeture, ancrage des anticipations) et rend compte de ce qui en dépend.
