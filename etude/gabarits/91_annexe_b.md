# Équations complètes du modèle (forme compacte) {#sec:annexe-b}

Cette annexe récapitule le système dans l'ordre de résolution d'une année (chapitre \ref{sec:annee}). Les numéros
renvoient aux sections du chapitre \ref{sec:equations}. Variables en logarithme en minuscules ; $\Delta$ : variation
annuelle ; $b$ : branche ($25$ branches marchandes) ; $j$ : produit ($64$).

**1. Crochets de régime ($t$, information $\le t-1$).**
$\Delta i_t = 0{,}728\,\Delta i_{t-1} + 0{,}393\,\Delta\pi^{ZE}_{t-1} + 0{,}302\,\Delta y^{ZE}_{t-1}$ ;
$\Delta B_t = \Delta B_{t-1} + 0{,}386\,(\Delta i_t - \Delta i_{t-1})$ ;
$\Delta \text{écart}_t = \gamma_d\,\Delta d_{t-1} + \gamma_s\,\Delta s_{t-1} + \text{chocs}$ ;
$\Delta i^m_t = (1 - 0{,}43)\,\Delta i^m_{t-1} + b^c_m \Delta i_t + b^l_m \Delta i^{OAT}_t$ ;
$\Delta i^e_t = (1 - 0{,}93)\,\Delta i^e_{t-1} + b^c_e \Delta i_t + b^l_e \Delta i^{OAT}_t$ ;
règle budgétaire $\Delta e_t = \text{clip}(\alpha(s^* - s^{ca}), 0, \bar e)$ ; objectif (lecture B)
$\Delta e^B_t = \text{clip}(c_t - s_{t-1}, -2, 2)$.

**2. Prix d'importation.** $\Delta p^m_{j,t} = \theta\,\Delta p^{*}_{j,t} + (1-\theta)\,\Delta p^{*}_{j,t-1}$,
$\theta \approx 0{,}5$.

**3. Salaires et prix.** $\Delta w_t = 0{,}39\,\Delta p^c_t - 0{,}09\,(w - p_{va} - \text{prod} - \mu_w)_{t-1} - \phi(u_t - u^*_t) + \dots$ ;
$p^*_{va,b} = \theta_b \ln \text{CSU}_b + (1-\theta_b) \ln(p_I K_{b,t-1}/Q_b)$ ; correction d'erreur des prix de VA ;
$p_j = \sum_i a^d_{ij} p_i + \sum_i a^m_{ij} p^m_i + v_j p_{va,j} + \tau_j$.

**4. Emploi et investissement.** $n_b = q_b - \sigma \ln(c_h/p_{va}) - (1-\sigma)(\ln E + \ln d)$ (dynamique partielle) ;
$\Delta i_b = 0{,}67\,\Delta q_b + 0{,}26\,\Delta q_{b,t-1} - \lambda_I(i_b - k^*_b)_{t-1} + \theta_T\,\Delta\text{Ép.}/I$ ;
$k^* = q - \sigma_K \ln c_K$.

**5. Revenus et demande.** $\text{RDB} = $ salaires $+$ revenus mixtes $+$ revenus de la propriété (dividendes M21) $+$
prestations (dont pensions M9) $-$ impôts et cotisations ;
$\Delta c = 0{,}85\,\Delta r - 0{,}22\,(c - r - \mu_c)_{t-1} - \psi_u \Delta u - \psi_r \Delta i^{m,r}$ ;
logement ; exportations $\Delta x = 0{,}71\,\Delta d^* - 0{,}60\,\Delta\ln(p_X/p^*)$ ; fermeture
$S_t = S_{t-1} - \rho\,\tilde y_{t-1} + \theta\,\Delta y^*$.

**6. Importations et production.** $\Delta m = 1{,}47\,\Delta \bar d - \lambda_M(m - 1{,}37\,\bar d - 0{,}006\,t + 0{,}16 \ln p_M/p)_{t-1}$ ;
$q = (I - A_d)^{-1} d_d$.

**7. Après convergence.** Potentiel CES ; $\tilde y = 100\ln(Y/Y^*)$ ; finances publiques (recettes par taux apparents,
dépenses, intérêts par cohortes M17, $D_t = D_{t-1} - \text{Solde}_t + \text{AF}_t$) ; compte des sociétés (intérêts,
IS, dividendes $0{,}364\,\Pi_{t-1}$, dette $+1{,}06 \sum \Delta \text{BF}$) ; comptes d'agents (RNB, capacités de
financement).

**8. Démographie et retraites (M1, M9).** Population Insee 2026 ; activité des seniors
$a(x,t) = A_s(t)\,\tilde h(x + 0{,}5 - \pi_{g,s})$, $\pi_{g,s} = \beta_s \text{AOD}_g + (1-\beta_s)\,62 + \varepsilon_s \Delta D_g / 4$ ;
pensions par génération, facteur de durée $f_{g,s}$ ; liens : population active, emploi des seniors, écart de masse
des pensions $\times 0{,}55$.
