# Équations et mécanismes économiques {#sec:equations}

Ce chapitre présente les équations du modèle dans la configuration de référence P4. Pour chacune, on indique sa
signification, ses variables et unités, son origine théorique, sa méthode d'estimation ou de calibration,
l'interprétation de ses paramètres, la sensibilité des résultats, ses limites et les formulations alternatives. Les
notations suivent une convention simple : les minuscules désignent des logarithmes ($y = \ln Y$), $\Delta$ la
variation d'une année à l'autre, l'indice $b$ la branche, $t$ l'année. Les coefficients estimés le sont sur
1997-2019 (hors années de crise sanitaire) sauf mention contraire. L'annexe \ref{sec:annexe-b} reprend l'ensemble sous
forme compacte.

**Comment lire une équation à correction d'erreur.** La plupart des équations de comportement ont la forme

$$\Delta x_t = \underbrace{\sum_k a_k \,\Delta z_{k,t}}_{\text{dynamique de court terme}}
\;-\; \lambda \,\underbrace{\left(x_{t-1} - x^*_{t-1}\right)}_{\text{écart à la cible}}, \qquad
x^*_t = \sum_k b_k z_{k,t} + \text{constante},$$

où $x^*$ est la valeur de long terme (la « cible ») déterminée par la théorie, et $\lambda$ la vitesse de retour vers
cette cible (la fraction de l'écart résorbée chaque année). Cette forme, popularisée par Engle et Granger (1987),
concilie une relation de long terme théorique et une dynamique de court terme ajustée aux données. Elle est celle des
modèles Mésange (Insee, DG Trésor) et FR-BDF (Banque de France) pour leurs blocs d'équations de comportement.

## Production et PIB potentiel {#sec:eq-production}

**Fonction de production.** Le potentiel des branches marchandes est représenté par une fonction CES (élasticité de
substitution constante) normalisée en heures :

$$Q^* = \left[\alpha\,(K)^{\frac{\sigma-1}{\sigma}} + (1-\alpha)\,(E\,H)^{\frac{\sigma-1}{\sigma}}\right]^{\frac{\sigma}{\sigma-1}},$$

où $Q^*$ est la valeur ajoutée potentielle (volume, euros de l'année de base), $K$ le capital (volume net), $H$ les
heures travaillées au chômage structurel, $E$ l'efficience du travail (tendance), $\alpha = 0{,}35$ la part du capital
[A, comptes nationaux] et $\sigma = 0{,}45$ l'élasticité de substitution capital-travail [C]. Le potentiel non
marchand (administrations, éducation, santé, action sociale, loyers) est égal à sa valeur ajoutée tendancielle.

*Origine et alternatives.* La CES généralise la Cobb-Douglas ($\sigma = 1$) ; les estimations françaises et
européennes de $\sigma$ sont en majorité inférieures à 1 (entre 0,3 et 0,7). Une Cobb-Douglas donnerait une
substitution plus forte et des effets du coût du travail sur l'emploi plus importants.

*Sensibilité.* Deux environnements calibrés ($\sigma = 0{,}3$ et $\sigma = 0{,}6$) montrent que $\sigma$ change peu
les effets sur le PIB (au plus 0,05 point à 20 ans pour les stratégies de test) mais modifie le contenu en emplois et,
par là, la dette (jusqu'à 7 points de PIB à 20 ans) (section \ref{sec:robustesse-env}).

*Limites.* La productivité tendancielle est exogène ; les effets de l'éducation, de l'innovation ou des réformes
structurelles sur l'efficience ne sont pas représentés (sauf capital public et R&D, exploratoires).

**Écart de production.** $\tilde y_t = 100 \times \ln(Y_t / Y^*_t)$ (en %), où $Y$ est le PIB et $Y^*$ le PIB
potentiel.

**Fermeture d'offre.** Un supplément de demande $S_t$ ramène la production vers le potentiel :

$$S_t = S_{t-1} - \rho\,\tilde y_{t-1} + \theta\,\Delta y^*_t \cdot (\text{révision}),$$

avec $\rho = 0{,}2$ [B] et $\theta = 0{,}75$ [C]. Il représente les canaux de retour non modélisés (politique
monétaire avant M24, crédit, confiance). C'est l'équation la plus influente pour le passage du court au long terme
(section \ref{sec:fermeture}).

## Demande agrégée et multiplicateurs {#sec:eq-demande}

La demande finale en volume est la somme de la consommation des ménages $C$, de leur investissement en logement
$I^m$, de l'investissement des branches $I^b$, des autres investissements (administrations, institutions sans but
lucratif) $I^a$, de la consommation publique $G$, des exportations $X$ et du supplément de fermeture $S$ ; la
production de chaque produit est obtenue par l'inverse de Leontief :

$$q = (I - A_d)^{-1}\,d_d,$$

où $A_d$ est la matrice des coefficients techniques domestiques (64 produits, TES de l'Insee) et $d_d$ la demande
finale adressée à la production intérieure (après déduction des importations, réparties selon les contenus en
importations de chaque composante). Le multiplicateur n'est pas un paramètre : il résulte de l'ensemble du système
(propensions, contenus en importations, prélèvements, réactions des prix et de la fermeture). Le chapitre
\ref{sec:transmission} en donne les valeurs simulées.

## Consommation et épargne {#sec:eq-consommation}

$$\Delta c_t = 0{,}85\,\Delta r_t - 0{,}22\,\left(c_{t-1} - r_{t-1} - \mu_c\right) - \psi_u\,\Delta u_t - \psi_r\,\Delta i^{m,r}_t + \text{calage},$$

où $c$ est la consommation des ménages en volume (log), $r$ le revenu disponible brut réel (déflaté par le prix de la
consommation), $u$ le taux de chômage, $i^{m,r}$ le taux réel des crédits à l'habitat (M24), $\mu_c$ la constante de
long terme (propension moyenne). Élasticité de court terme au revenu 0,85 (t = 4,2) et vitesse de retour 0,22 [E] ;
épargne de précaution $\psi_u = 0{,}3\,\%$ par point de chômage (fourchette 0,1-0,6) et effet du taux réel
$\psi_r = 0{,}2$ (fourchette 0-0,5) [C].

*Interprétation.* À long terme, la consommation est proportionnelle au revenu disponible réel (élasticité unitaire,
taux d'épargne stable) ; à court terme, 85 % d'une variation de revenu passe dans la consommation la première année.
Ce comportement est intermédiaire entre la fonction de consommation keynésienne et le revenu permanent.

*Hétérogénéité.* Pour les mesures socio-fiscales, la variation de revenu de chaque décile est pondérée par une
propension marginale à consommer propre (plus élevée en bas de la distribution) ; l'écart à la propension moyenne
entre comme ajustement de consommation (M14).

*Limites et alternatives.* Pas d'effet de richesse (patrimoine immobilier et financier), pas d'anticipation des impôts
futurs (non ricardien), pas d'épargne de précaution liée à l'incertitude politique. Un modèle à agents hétérogènes
(HANK) ferait dépendre les propensions de la liquidité des ménages et de la nature du choc.

**Logement.** $\Delta i^m_t$ suit une équation estimée sur le revenu disponible réel [E] ; le taux du crédit à
l'habitat n'y entre pas (testé et non retenu, section \ref{sec:donnees}).

**Taux d'épargne.** $s_t = 1 - P_C\,C_t / R_t$ en résulte (avec la correction des revenus du patrimoine et de
l'investissement des ménages).

## Investissement {#sec:eq-investissement}

$$\Delta i^b_{t} = 0{,}67\,\Delta q^b_{t} + 0{,}26\,\Delta q^b_{t-1} - \lambda_I\left(i^b_{t-1} - k^{*b}_{t-1}\right) + \theta_T\,\frac{\Delta \text{Épargne}^{S11}_{t}}{I_{t-1}} + \text{calage},$$

$$k^{*}_t = q_t - \sigma_K \ln c_{K,t}, \qquad c_{K,t} = \frac{p_I}{p_Q}\,\frac{\left(i^{e,r}_t + \delta\right)\left(1 - z\,\tau^{IS}_t\right)}{1 - \tau^{IS}_t},$$

où $i^b$ est l'investissement de la branche (log), $q^b$ sa production, $k^*$ le capital désiré, $c_K$ le coût d'usage
du capital, $i^{e,r}$ le taux réel des crédits aux sociétés (M24), $\delta$ la dépréciation, $\tau^{IS}$ le taux de
l'impôt sur les sociétés (semi-élasticité des bénéfices au taux pour les groupes : 0,8 [B]). Accélérateur estimé
(0,67 ; 0,26) [E] ; élasticité au coût d'usage −0,18 pour l'agrégat des sociétés non financières [E, fragile] ; canal
de trésorerie $\theta_T = 0{,}10$ [C].

*Limites.* L'investissement des sociétés est l'équation la moins bien validée (erreur de niveau de 11 % en 2024 dans
le test hors échantillon) ; l'incertitude politique et réglementaire n'y figure pas.

## Emploi, chômage, salaires et offre de travail {#sec:eq-travail}

**Demande de travail (branches marchandes).** À production donnée, la condition du premier ordre de la CES donne

$$n^b_t = q^b_t - \sigma \ln\left(\frac{c_{h,t}}{p_{va,t}}\right) - (1-\sigma)\left(\ln E_t + \ln d_t\right),$$

où $n$ est l'emploi (heures, puis personnes via la durée $d$), $c_h$ le coût horaire du travail (rémunérations moins
subventions sur salaires) et $p_{va}$ le prix de la valeur ajoutée. La dynamique de court terme (élasticité à la
production 0,26, retour de 21 % par an dans l'équation estimée) lisse l'ajustement [E]. **Emploi non marchand :**
volume de valeur ajoutée divisé par une productivité tendancielle propre.

**Population active.** Somme des actifs de 15 à 74 ans : taux d'activité par âge et sexe observés jusqu'à 54 ans,
modèle des seniors au-delà (M9, section \ref{sec:eq-retraites}), effets de participation des réformes des prestations
(M15 : élasticité de participation 0,2, d'heures 0,1 [B]).

**Chômage.** $u_t = 1 - N_t / PA_t$ ; le chômage structurel $u^*$ est exogène (7,5 % puis 7,0 %) sauf effets de
l'assurance chômage ($+0{,}063$ point par 10 % d'allocations [B]) et de la formation [X].

**Salaires (secteur marchand, par tête).**

$$\Delta w_t = 0{,}39\,\Delta p^c_t + \text{(productivité)} - 0{,}09\left(w_{t-1} - p_{va,t-1} - \text{prod}_{t-1} - \mu_w\right) - \phi\,(u_t - u^*_t) + \text{calage},$$

où $w$ est le salaire moyen par tête, $p^c$ le prix de la consommation, la cible de long terme étant une part des
salaires dans la valeur ajoutée stable (retour de 9 % par an) [E] ; $\phi = 0{,}004$ par point d'écart de chômage [C,
non identifié en annuel et en trimestriel], multiplié par 0,5 quand le chômage est au-dessus de son niveau structurel
(rigidité à la baisse) [C]. Le SMIC suit sa règle légale (inflation des 20 % de ménages les plus modestes et moitié du
gain de pouvoir d'achat du salaire horaire de base ouvrier et employé), avec diffusion de 11 % de ses hausses à la
masse salariale [H].

*Alternatives.* Une courbe de Phillips plus pentue (ancrage faible : $\times 2$) ou une indexation plus rapide
modifient surtout les prix et la compétitivité ; elles sont testées en régime de robustesse.

## Prix et inflation {#sec:eq-prix}

**Prix de la valeur ajoutée (frontière des prix des facteurs, P4).**

$$p^{*}_{va,b,t} = \theta_b \ln \text{CSU}_{b,t} + (1-\theta_b)\,\ln\left(\frac{p_{I,t}\,K_{b,t-1}}{Q_{b,t}}\right),$$

$$\Delta p_{va,b,t} = a_1\,\Delta \ln \text{CSU}_{b,t} + a_2\,\Delta q_{b,t} - \lambda_p\left(p_{va,b,t-1} - p^*_{va,b,t-1}\right) + \kappa\,\tilde y_t\,\mathbb{1}_{\text{hors industrie}},$$

où CSU est le coût salarial unitaire, $\theta_b$ la part du travail de la branche (médiane 1997-2019) [D], et
$\kappa = 0{,}10$ la pente sur l'écart de production hors industrie [C]. Les coefficients de court terme et la vitesse
de retour sont estimés en panel [E]. Une variante (équation v0.9, marge vers sa norme, transmission du CSU 0,67)
dispose de son propre environnement calibré.

**Prix de production et de consommation (Leontief).** Pour chaque produit $j$,

$$p_j = \sum_i a_{ij}^d\,p_i + \sum_i a_{ij}^m\,p^m_i + v_j\,p_{va,j} + \tau_j,$$

où $a^d$ et $a^m$ sont les coefficients techniques domestiques et importés, $p^m$ les prix d'importation (transmission
partielle des prix mondiaux, la moitié l'année même [E]), $v$ la part de la valeur ajoutée et $\tau$ les impôts nets
sur les produits. Le prix de la consommation est la moyenne pondérée par la structure de la consommation.

*Limites.* Pas de distinction des taux de TVA par produit énergétique ; pas de substitution entre énergies ; les
grands chocs de prix (2022-2023) sont mal reproduits.

## Productivité {#sec:eq-productivite}

La productivité tendancielle de chaque branche (croissance moyenne de la productivité par tête sur les huit dernières
années observées hors 2020-2021) est un paramètre [D/H] ; la convention de dépense de la référence retient 0,7 % par an
pour la croissance potentielle conventionnelle. Deux canaux endogènes : capital public (élasticité 0,08, capital
public net de 55 % du PIB, dépréciation 4 % par an) [C] et R&D (additionnalité 0,7 €/€, élasticité au stock 0,08)
[X]. La durée du travail modifie la productivité horaire (70 % d'une baisse de durée absorbée sans embauche, calé sur
l'ordre de grandeur des 35 heures [H] ; appliqué symétriquement aux hausses).

## Fiscalité et transferts {#sec:eq-fiscalite}

Les recettes publiques sont calculées par **taux apparents** appliqués à des assiettes simulées :

- impôts sur les produits (TVA et accises) : taux apparent × consommation des ménages (et autres emplois taxés) ;
  variation de taux répercutée à 80 % sur les prix (95 % pour les hausses et 50 % pour les baisses du taux normal,
  d'après Benzarti et al., 2020) [B] ;
- impôts des ménages (impôt sur le revenu, CSG, autres) : taux apparent × revenus ; mesures en points de PIB
  (`impots_menages_pib`) ou par microsimulation ;
- cotisations sociales : taux apparents × masse salariale ; transmission des cotisations employeurs aux salaires
  0,5 à long terme [C] ;
- impôt sur les sociétés : compte des sociétés (section \ref{sec:eq-societes}) ;
- impôts de production : répercussion de 50 % sur les prix de la valeur ajoutée, incidence de 20 % sur les salaires
  [D, hypothèse] ;
- autres recettes proportionnelles au PIB nominal.

Les **prestations** (hors pensions) sont indexées sur les prix de l'année précédente et, dans la convention « part
constante », croissent avec le PIB potentiel conventionnel ; les allocations chômage sont proportionnelles au nombre
de chômeurs ; les pensions de droit direct viennent de M9.

## Dépenses publiques {#sec:eq-depenses}

$$\text{Dép}_t = \underbrace{W^{pub}_t\,N^{pub}_t}_{\text{rémunérations}} + \underbrace{P_{G,t}\,G^{autres}_t}_{\text{consommation hors rémunérations}} + \underbrace{\text{Prest}_t}_{\text{prestations}} + \underbrace{\text{Int}_t}_{\text{intérêts}} + \underbrace{\omega_t\,Y^{nom}_t}_{\text{autres dépenses}} + \text{calage},$$

où $W^{pub}$ est le salaire public (instrument : point d'indice), $N^{pub}$ l'emploi public (non marchand), $G^{autres}$
la consommation publique hors rémunérations en volume, $\omega$ la part du PIB des autres dépenses (subventions,
investissement public, autres transferts). Convention de référence « part constante » : consommation publique et
prestations hors pensions croissent comme le PIB potentiel conventionnel (population active × (1 − u*) ×
productivité de 0,7 %) [H, décision du projet].

## Retraites {#sec:eq-retraites}

**Âge d'ouverture des droits (AOD)** par génération $g$ : législation actuelle (loi de 2023 aménagée par la LFSS pour
2026 : 62 ans et 9 mois pour les générations 1963-1964, puis +3 mois par génération jusqu'à 64 ans pour 1969) [D],
ou réforme « cible à partir de l'année de début, progressive ou immédiate ».

**Durée d'assurance requise** $D_g$ (trimestres) : 170 pour 1963-1964, 171 pour 1965, 172 à partir de 1966 en
législation actuelle [D] ; calendrier de la loi de 2014 (un trimestre toutes les trois générations jusqu'à 172 pour
1973) pour l'abrogation de la réforme de 2023 ; cible d'une réforme (immédiate ou un trimestre par génération).

**Âge pivot et activité des seniors.** Pour le sexe $s$ et la génération $g$,

$$\pi_{g,s} = \beta_s\,\text{AOD}_g + (1 - \beta_s)\cdot 62 + \varepsilon_s\,\frac{D_g - D^{act}_g}{4}, \qquad
a(x,t) = A_s(t)\cdot h\big(x + 0{,}5 - \pi_{g,s}\big),$$

$$h(d) = \begin{cases} 1 - e(t)\,\min\left(1, \frac{d+5}{5}\right)^+ & d < 0 \\ s\,e^{-k d}\,(1 - e(t)) & d \ge 0 \end{cases}$$

où $a(x,t)$ est le taux d'activité à l'âge $x$ relatif à celui des 50-54 ans $A_s(t)$, $e(t)$ la part des sorties
précoces (tendance arrêtée en 2025), $s$ et $k$ la marche et la décroissance après l'âge pivot, $\beta_s$ la part du
profil qui se décale avec l'AOD — tous estimés par moindres carrés non linéaires sur les taux d'activité par tranche
quinquennale de 2003 à 2019 [E]. $\varepsilon_H = 0{,}75$ et $\varepsilon_F = 5/12$ (report de 9 et 5 mois par année
de durée supplémentaire, Bozio, 2011) [E, littérature, appliqué symétriquement aux baisses : H].

**Groupes particuliers.** Pour une fraction $p$ de chaque génération (carrières longues à l'âge $a_{CL}$, ou maintien
des conditions actuelles), le profil devient, en écart à la législation actuelle,

$$\tilde h = h(d_{reg}) + p\left[h(d_{grp}) - h(d_{reg})\right] - p\left[h(d^{act}_{grp}) - h(d^{act})\right],$$

ce qui reproduit exactement le profil estimé en législation actuelle. L'âge actuel du groupe « carrière longue » est
approché par $\max(60, \text{AOD} - 2)$ [H] ; $p = 0{,}17$ pour les carrières longues (part des départs anticipés
pour carrière longue au régime général en 2024, CNAV) [D, approchant l'éligibilité].

**Pensions.** Pension moyenne de la génération à la liquidation $= \nu \times$ moyenne des 25 derniers salaires moyens
revalorisés sur les prix, puis revalorisée sur les prix ; masse $= \sum_{x,s}$ retraités $\times$ pension. Le facteur
de durée

$$f_{g,s} = 1 - \phi_{base}\,(1 - \varepsilon_s)\,\Delta D_g \left(\frac{4}{D^{act}_g} + 0{,}05\right)$$

applique la proratisation et la décote (1,25 % par trimestre [D]) à la part de base de la pension ($\phi_{base} = 0{,}5$
[H]) pour la fraction des assurés qui ne reportent pas leur départ. L'écart de masse dû à une réforme d'âge est
multiplié par 0,55 (calage sur les chiffrages de l'étude d'impact de 2023 et de l'Institut Montaigne : les départs
déplacés concernent surtout des carrières incomplètes) [C].

*Limites.* Pas de distinction des régimes, de la réversion, de la surcote, des minima de pension ; pas de piliers de
capitalisation ; les durées validées individuelles ne sont pas simulées (effet moyen par génération et sexe).

## Dette et intérêts {#sec:eq-dette}

$$D_t = D_{t-1} - \text{Solde}_t + \text{AF}_t, \qquad \text{Int}_t = \sum_{c} r_c\,B_{c,t}, $$

où la dette $D$ (au sens de Maastricht) évolue avec le besoin de financement et des ajustements stock-flux
$\text{AF}$ observés jusqu'en 2025 (nuls ensuite) ; la charge d'intérêts est la somme, sur les cohortes d'émission
$c$, du taux à l'émission $r_c$ (courbe des taux) appliqué à l'encours restant $B_{c,t}$ (module M17, validé sur les
données de l'Agence France Trésor) [D/E]. Le **taux apparent** rejoint ainsi progressivement le taux de marché, au
rythme du renouvellement de la dette (durée moyenne de l'ordre de 8 ans). La boucle intra-annuelle intègre le besoin
de financement de l'année.

## Politique monétaire {#sec:eq-monetaire}

En écart à la référence (années $\ge 2027$, information de $t-1$) :

$$\Delta i_t = 0{,}728\,\Delta i_{t-1} + 0{,}393\,\Delta\pi^{ZE}_{t-1} + 0{,}302\,\Delta y^{ZE}_{t-1},$$

$$\Delta\pi^{ZE} = \omega_{FR}\,\Delta\pi^{FR} + (1-\omega_{FR})\,\text{choc}^\pi, \qquad \Delta y^{ZE} = \omega_{FR}\,\Delta y^{FR} + (1-\omega_{FR})\,\text{choc}^y,$$

où $i$ est le taux directeur, $\pi$ l'inflation, $y$ l'écart d'activité (écart du PIB à la référence, ou loi d'Okun
sur le chômage en variante) et $\omega_{FR}$ le poids de la France [E : règle estimée sous forme contemporaine sur des
données annuelles de la zone euro, appliquée avec un an de décalage car la forme retardée estimée avait un signe
erroné]. Variante : anticipations rationnelles du taux allemand sous la règle.

*Lecture.* Avec un poids de 20 % de la France, une hausse de 1 point de l'inflation française n'induit qu'environ
0,08 point de hausse du taux directeur la première année. La politique monétaire commune amortit peu les chocs
nationaux, ce qui rapproche la France d'une économie en change fixe pour son budget.

## Taux de crédit {#sec:eq-credit}

$$\Delta i^{m}_t = (1 - v_m)\,\Delta i^m_{t-1} + b^c_m\,\Delta i_t + b^l_m\,\Delta i^{OAT}_t, \qquad
\Delta i^{e}_t = (1 - v_e)\,\Delta i^e_{t-1} + b^c_e\,\Delta i_t + b^l_e\,\Delta i^{OAT}_t,$$

(en écart à la référence), avec pour l'habitat une vitesse $v_m = 0{,}43$ et une transmission de long terme de 0,90,
et pour les sociétés non financières $v_e = 0{,}93$ et 0,78 [E, séries MIR de la BCE]. Le crédit aux sociétés,
majoritairement à taux variable ou court, s'ajuste presque immédiatement ; le crédit à l'habitat, à taux fixe, plus
lentement.

## Prime de risque souveraine {#sec:eq-prime}

$$\Delta(\text{OAT} - \text{Bund})_t = \gamma_d\,\Delta d_{t-1} + \gamma_s\,\Delta s_{t-1} + \text{chocs}_t,$$

où $\Delta d$ et $\Delta s$ sont les écarts du ratio de dette et du solde public à la référence ; $\gamma_d = 0{,}013$
et $\gamma_s = -0{,}0148$ (points de taux par point de PIB) hors crise, $\gamma_d = 0{,}012$ et $\gamma_s = -0{,}118$ en
incluant 2010-2013 [E, panel de la zone euro, effets fixes par pays]. Le coefficient de solde est fragile.
Variante en niveau au-delà d'un seuil de dette [H].

*Littérature.* Les études empiriques trouvent en général 2 à 5 points de base par point de dette en moyenne, avec de
fortes non-linéarités et une dépendance au contexte (liquidité, appartenance à l'union monétaire, programme de la BCE).

## Économie extérieure {#sec:eq-exterieur}

$$\Delta x_t = 0{,}71\,\Delta d^*_t - 0{,}60\,\Delta\ln\left(\frac{p_X}{p^*}\right)_t + \text{calage},$$
$$\Delta m_t = 1{,}47\,\Delta \bar d_t - \lambda_M\left(m_{t-1} - 1{,}37\,\bar d_{t-1} - 0{,}006\,t + 0{,}16\,\ln\frac{p_M}{p}_{t-1}\right),$$

où $x$ et $m$ sont les exportations et importations en volume, $d^*$ la demande mondiale adressée, $\bar d$ la demande
intérieure pondérée par les contenus en importations, $p_X/p^*$ la compétitivité-prix [E]. Le revenu national brut
est le PIB augmenté des revenus primaires nets du reste du monde (indexés sur le PIB nominal, diminués de l'écart des
dividendes versés aux non-résidents, 50 % des dividendes des sociétés).

## Compte des sociétés non financières {#sec:eq-societes}

$$\text{Int}^{S11}_t = \rho_t\,D^{S11}_{t-1}, \qquad \rho_t = \rho_{t-1} + \mu\left(\rho^*_t - \rho_{t-1}\right), \qquad \rho^*_t = c_\rho + 1{,}29\left(0{,}77\,i^{c}_t + 0{,}23\,i^{l}_t\right),$$
$$\text{IS}_t = \tau^{app}\,\text{RCAI}_t\cdot f^{fisc}_t, \qquad \text{Div}_t = 0{,}364\,\Pi_{t-1}, \qquad
D^{S11}_t = D^{S11,base}_t + 1{,}06\sum_{k \le t}\left(\text{BF}_k - \text{BF}^{base}_k\right),$$

où $\rho$ est le taux apparent de la dette des sociétés, qui rejoint à la vitesse $\mu = 0{,}60$ [E, 1999-2024] un taux de
marché $\rho^*$ combinant taux court (poids 0,77) et long, avec une transmission de 1,29 et un écart moyen de 3,4 points
[E], RCAI le résultat courant avant impôt, $\Pi$ le résultat après intérêts et impôt, BF le besoin de
financement. Les intérêts reçus valent 0,77 fois les intérêts versés [C] ; les dividendes sont répartis entre ménages
(42 %), reste du monde (50 %) et administrations (8 %) [D]. L'équation de Lintner (lissage des dividendes) n'est pas
identifiée : la règle proportionnelle est retenue, avec un paramètre de lissage en variante [H].

## Distribution des revenus {#sec:eq-distribution}

Pour une mesure socio-fiscale, la variation du revenu disponible du ménage $h$ est
$\Delta R_h = -\Delta T_h + \Delta B_h$ (impôts $T$, prestations $B$), calculée par OpenFisca sur les revenus de 2024 ;
elle est agrégée par décile de niveau de vie $q$ (revenu disponible par unité de consommation, échelle de l'OCDE
modifiée) :

$$\Delta R_q = \sum_{h \in q} w_h\,\Delta R_h, \qquad \Delta C^{M14} = \sum_q (\text{pmc}_q - \overline{\text{pmc}})\,\Delta R_q,$$

où $w_h$ est le poids de sondage et pmc la propension marginale à consommer du décile. Les indicateurs d'inégalité
(rapports interdéciles, Gini) sont calculés avant et après réforme. Les effets macroéconomiques induits (emploi,
salaires, prix) ne sont pas redistribués ménage par ménage dans les résultats de cette étude.
