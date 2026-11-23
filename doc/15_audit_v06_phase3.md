# 15 — Audit de la version 0.6 (phase 3, étape 1-2)

Statut : document d'audit. Les chiffres cités proviennent de simulations **exécutées**
(`phase3/diagnostic_fermeture.py`, sortie `phase3/resultats/diagnostic_v06.json`) sur l'instantané
figé de la v0.6 (`modele_v06/`). Les corrections proposées sont implémentées en v0.7 ; leur
vérification fait l'objet du document 17.

## 1. Le paradoxe de fermeture

Deux chocs d'offre défavorables ont été appliqués au compte de référence v0.6 (écarts en 2037) :

| Choc | PIB vol. | Emploi | Chômage | Prix | Dette/PIB | Solde/PIB |
|---|---|---|---|---|---|---|
| Productivité −0,3 pt/an dès 2028, fermeture centrale | −0,87 % | +0,47 % | −0,43 pt | +1,67 % | −4,5 pt | +0,40 pt |
| Idem, sans fermeture (ρ = 0) | −0,11 % | — | −1,06 pt | — | −8,4 pt | — |
| Population active −0,2 %/an | −1,13 % | — | −0,95 pt | +1,45 % | −1,37 pt | — |

Un choc qui devrait appauvrir le pays (le PIB potentiel baisse d'environ 2,7 % en 2037 pour le
choc de productivité) **réduit** le chômage et la dette. Ce résultat est contraire à la théorie
et à l'expérience (ralentissement de la productivité après 2008 et après 2019 : hausse du ratio
de dette, pas baisse).

## 2. Cause structurelle (et non symptôme)

L'enchaînement, vérifié équation par équation :

1. **Pas de production potentielle.** Le PIB est entièrement déterminé par la demande ; l'offre
   n'intervient que via le taux d'utilisation des capacités de l'industrie (TUC).
2. **Le choc de productivité n'entre que dans l'équation d'emploi** : pour la même demande, il faut
   plus de salariés. L'emploi monte, le chômage baisse.
3. **La fermeture agit sur l'écart de chômage (u − u\*)**, pas sur l'écart de production. Elle voit
   un chômage « trop bas » et resserre la demande, mais ne voit jamais que la capacité de produire
   a baissé.
4. **La boucle prix-salaires** (Phillips sur salaires) gonfle les salaires et les prix ; le PIB
   **nominal** augmente (+1,7 % en 2037) alors que le PIB réel baisse. Les recettes suivent le
   nominal, les dépenses (indexées avec retard, ou fixées en volume) moins : le solde s'améliore,
   et le ratio dette / PIB nominal baisse mécaniquement. C'est un effet d'« inflation tax »
   non borné.
5. **Incohérence u\*** : u\* = 7,5 % dans la fermeture alors que la référence converge vers 7,0 %.
   La fermeture pousse donc en permanence la demande à la baisse dans la référence, compensée par
   les termes de calage ; tout choc qui modifie le chômage interagit avec ce biais.
6. **Stabilisateur chômage absent** : l'indemnisation n'était pas reliée au nombre de chômeurs
   (la documentation du code l'affirmait à tort). Une hausse du chômage ne coûtait rien aux
   finances publiques.
7. **Pas de courbe de Phillips sur les prix hors industrie**, pas d'effet de tension des capacités
   sur les importations : un excès de demande ne se traduisait pas en inflation ni en fuites.

## 3. Inventaire des défauts et priorités

| # | Défaut | Conséquence | Priorité | Traitement v0.7 |
|---|---|---|---|---|
| 1 | Fermeture sur u au lieu de l'écart de production | Paradoxe des chocs d'offre | Critique | PIB potentiel Cobb-Douglas, fermeture sur l'écart de production |
| 2 | u\* incohérent avec la référence | Biais permanent | Critique | Trajectoire u\* 7,5 → 7,0 (2026-2031) |
| 3 | Indemnisation chômage non liée au chômage | Pas de stabilisateur | Élevée | Dépense ARE ∝ nombre de chômeurs (1,5 % du PIB de base) |
| 4 | Pas de Phillips prix hors industrie ; importations insensibles aux tensions | Surchauffe sans inflation | Élevée | κ = 0,10 ; μ = 1,0 |
| 5 | TVA répercutée à 80 %, symétrique, immédiatement | Surestime l'effet prix des baisses | Élevée | Répercussion asymétrique et progressive (littérature Benzarti et al.) |
| 6 | IS sans transfert de bénéfices | Surestime le rendement des hausses d'IS | Élevée | Semi-élasticité 0,8 sur la part multinationale |
| 7 | Bénéfices conservés sans usage | Les baisses d'IS restent sans effet ou sont mécaniquement investies selon le levier | Moyenne | Réinvestissement de 10 % de la trésorerie (borne basse : 0) |
| 8 | Pas de délocalisation liée à l'énergie | Chocs énergie sous-estimés pour l'industrie lourde | Moyenne | Élasticité 0,15 sur 4 produits énergo-intensifs |
| 9 | Offre de travail exogène (RSA et prime d'activité ont le même effet) | Faux pour les prestations | Élevée | Module M15 (OpenFisca, marge extensive et intensive) |
| 10 | Effet de l'assurance chômage sur u\* arbitraire | Non documenté | Moyenne | Élasticité de durée 0,3 (Le Barbanchon et al.) |
| 11 | Pas d'épargne de précaution ni d'effet du taux réel sur la consommation | Multiplicateurs trop stables | Moyenne | ψ_u = 0,3 ; ψ_r = 0,2 |
| 12 | Salaires symétriques | Désinflation trop facile en récession | Moyenne | Rigidité à la baisse (×0,5) |
| 13 | Dépense publique non différenciée (R&D, formation) | Leviers d'offre absents | Moyenne | Leviers « recherche » et « formation », exploratoires |
| 14 | Convention « autres dépenses ∝ PIB nominal » | Masque une part de l'effet des chocs | Faible | Conservée, documentée |
| 15 | Microsimulation statique | Pas de rétroaction des comportements individuels | Moyenne | M15 partiel ; reste un chantier |
| 16 | Solde extérieur en niveau peu fiable | Seuls les écarts sont utilisables | Faible | Inchangé, signalé |
| 17 | Pas de bilans (patrimoine, dette privée) | Pas d'effets de richesse ni de désendettement | Faible à moyenne | Non traité (hors périmètre) |
| 18 | Termes de calage imposant la trajectoire de référence | Les écarts sont fiables, les niveaux dépendent des hypothèses | Information | Recalés en v0.7 |

## 4. Ce que la correction doit garantir (tests)

- Un choc de productivité ou de population active défavorable **réduit** le PIB vers le PIB potentiel
  et **augmente** le ratio de dette à moyen terme ; le chômage revient vers u\*.
- La référence n'est pas modifiée par la nouvelle fermeture (l'écart de production y est nul par
  construction de la productivité globale des facteurs implicite).
- Les baisses de TVA sont moins répercutées que les hausses.
- Une baisse d'IS n'augmente pas automatiquement l'investissement au-delà du canal trésorerie.
- Une hausse de prime d'activité augmente la population active ; une hausse de RSA la réduit.

## 5. Validation externe disponible

Le CICE (environ 20 Md€) est estimé à 100 000-160 000 emplois (France Stratégie, 2020). La v0.6
donnait +86 000 à +109 000 emplois pour une baisse de cotisations de 20 Md€ : ordre de grandeur
compatible, plutôt dans le bas de la fourchette. Ce point sert de repère pour la v0.7.
