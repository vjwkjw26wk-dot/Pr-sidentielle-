# Phase 4.2 — A.2 : ancrage nominal, boucle prix-salaires, coût du capital (note de décision)

Branche `phase42a2`. La v0.9 reste reproductible par défaut (tests `tests/test_phase42.py`, 6/6).

## 1. Diagnostic de l'ancrage nominal

- Structure : prix de VA = marge sur le coût salarial unitaire (homogène) ; salaires = part salariale en prix de VA
  (homogène) ; prix à la consommation = prix domestiques et importés. Dans une union monétaire, le niveau des prix
  domestiques n'est rattaché au niveau européen que par la compétitivité (prix relatifs → exportations → activité →
  chômage → salaires) et par la courbe de Phillips.
- Choc salarial temporaire (b1, b2) : l'inflation revient à la base en 4-5 ans ; le niveau des prix se déplace de façon
  permanente et finie (« hystérèse de niveau ») ; les variables réelles (marge, part salariale) convergent. La fermeture
  n'est PAS responsable (hypothèse réfutée). Le canal de compétitivité est faible : −0,7 à −1 % d'exportations, chômage
  inchangé. Artefact corrigé : un choc qui remplaçait la bascule CICE 2019 au lieu de s'y ajouter.
- Défaut démontré (b6) : l'effet du taux d'utilisation des capacités (TUC) sur les prix de VA de l'industrie, en niveau
  dans une équation en croissance, transforme une baisse durable du capital (choc de taux) en inflation croissante
  (prix +14 à +22 % la 15e année). Le coefficient n'est pas significatif (0,001 ± 0,001 par point). Option
  `tension_prix = "aucune"`. La variante « capacité au capital désiré » ne règle pas le problème (déflation inverse).
- Restent faibles : canal de compétitivité ; pente de Phillips (calibrée, non identifiée en trimestriel) ; un choc de
  demande permanent qui maintient le chômage sous u* produit une inflation durable (+0,3 à +0,5 pt/an).

## 2. Économétrie trimestrielle (M20, b3)

- Salaires : indexation contemporaine 0,28 (0,12) ; indexation cumulée instable entre régimes (0,80 avant 2008, 0,07
  après 2010) ; pente de Phillips nulle et non identifiée ; anticipations des ménages non significatives.
- Prix de VA (agrégat marchand, trimestriel) : transmission du CSU faible et instable, correction d'erreur de mauvais
  signe : non utilisable. Le panel annuel de 25 branches reste la meilleure source pour cette équation.
- Système conjoint hors échantillon 2021-2024 : salaires et prix sous-estimés de 6 à 8 % en niveau (épisode hors du
  régime estimé : énergie, anticipations, marges).
- Équivalent annuel de la dynamique salariale : 0,39 la 1re année (= coefficient annuel v0.9) + rattrapage ≈ 0,17.

## 3. Coût du capital (b4)

- Estimation libre : poids du coût du capital nul (avec le taux observé : −0,08 ; avec un taux réel normatif : −0,18,
  non significatif) ; poids du CSU 0,77-0,94. Pas de canal « taux d'intérêt → prix » dans les données.
- Frontière des prix de facteurs imposée (θ_b = part du travail de la branche, coût du capital au prix de
  l'investissement à taux normatif) : ajustement identique à la v0.9 hors échantillon (RMSE 2,05 contre 2,08 ;
  9,88 contre 9,90). Choix théorique, non contredit par les données hors échantillon.

## 4. Transmission des baisses de coût du travail (b4)

- Subventions (CICE) transmises comme les autres variations de coût (0,79 ± 0,13 contre 0,73 ; égalité non rejetée,
  identification faible : taux uniforme). Aucune hétérogénéité significative selon la tension, l'exposition, la marge
  initiale ; pas d'asymétrie.
- Conséquence : la répartition des gains n'est pas identifiable par branche avec ces données ; elle est déterminée par
  l'architecture de long terme. v0.9 : ≈ 80 % aux prix à long terme. Frontière : ≈ 45-60 %, le reste en marges puis en
  salaires réels — plus proche des évaluations du CICE.

## 5. Candidates (backtests et chocs : `phase42/resultats/a6_*`, `phase42/a2/b5_*`)

| | v0.9 | T0 | T1 | T2 |
|---|---|---|---|---|
| Prix de VA | CSU | CSU | frontière | frontière |
| Effet TUC sur les prix | oui | non | non | non |
| Rattrapage salarial | non | non | non | 0,17 |
| Choc salarial temporaire, prix à 15 ans | +2,7 % (dérive) | +2,1 % | +1,5 % (stable) | |
| Choc de taux, prix à 15 ans | +13,7 % (emballement) | −3,1 % | −4,5 % | |
| Coût du travail −2 %, prix à 5 / 15 ans | −1,6 / −1,7 % | −1,6 / −1,4 % | −1,3 / −0,9 % | |
| Backtests | référence | ≈ v0.9 | meilleur 2014, 2021 ; moins bon 2010, 2012 | meilleur 2021 |

Recommandation : T1 comme candidate de référence pour le chantier B (cohérence avec la CES, meilleur ancrage,
répartition des baisses de coût plausible), T0 comme variante prudente, T2 comme variante d'indexation forte.
Validation définitive après le compte des sociétés et le protocole prédictif (chantier C).
