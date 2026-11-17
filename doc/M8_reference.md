# Trajectoire de référence « à politique inchangée » (M8, version 1.0, novembre 2026)

**État : opérationnel.** Code : `src/m8_reference.py`. Cette trajectoire remplace le compte central conventionnel des
versions précédentes (exogènes prolongés à rythme moyen, base 2022, non recalé). L'ancien compte faisait démarrer les
mesures en 2024 et l'interface n'affichait que des écarts, ce qui masquait la dynamique de l'économie (retours de
l'utilisateur du 17 novembre 2026).

Ce n'est pas une prévision. C'est le point de comparaison commun à toutes les mesures : aucune mesure nouvelle après
la loi de finances 2026, législation sociale et fiscale actuelle.

## 1. Construction

| Période | Méthode | Sources |
|---|---|---|
| 2023-2025 | Le modèle reproduit les comptes observés : consommation, investissement, exportations, importations, emploi, prix à la consommation, salaires, PIB en volume et en valeur, recettes, dépenses, dette publiques | Insee (comptes annuels, mai 2026), Eurostat |
| 2026-2031 | Croissance, chômage et inflation de la France : FMI. Solde public 2026 : FMI. Finances publiques ensuite calculées par le modèle | FMI, WEO octobre 2026 (API DataMapper) |
| après 2031 | Productivité par tête +0,7 %/an ; chômage convergeant vers 7 % (−0,3 point par an au plus) ; inflation de 2031 | COR, rapport annuel juin 2026 (scénario de référence) |

**Termes de calage.** Ils s'ajoutent aux taux de croissance des équations (consommation, investissement, exportations,
importations, emploi, prix de la valeur ajoutée, salaires). Des termes en niveau corrigent les stocks et le PIB
nominal ; d'autres termes portent sur les recettes et les dépenses publiques (points de PIB) et sur l'ajustement
stock-flux de la dette. Pour 2026-2035, seuls les termes de demande (consommation et investissement), d'emploi et de
prix sont calés, sur les cibles de croissance, de chômage et d'inflation. Les recettes et les dépenses suivent les
règles du modèle ; leur terme de calage reste à sa valeur de 2026.

**Ancrage des équations à correction d'erreur.** Sans précaution, les termes de rappel ramèneraient après 2025 le
modèle vers l'équilibre estimé sur 1997-2019 : l'emploi, par exemple, rattraperait un écart accumulé, ce qui
donnerait une productivité négative pendant plusieurs années. L'écart à l'équilibre constaté en fin 2025, mesuré
relativement à celui de l'année de base 2022, est donc supposé durable (`Exogenes.ancrage`). Cela concerne
l'emploi et les prix par branche, les salaires, la consommation et les importations.

## 2. Exogènes de projection

- **Démographie** (Insee, projection centrale) : population active et pensions de droit direct par génération (M9,
  législation actuelle). La masse des pensions est revalorisée sur les prix simulés. Les prestations hors pensions
  augmentent à leur rythme moyen 2011-2019, soit +1,4 %/an en volume.
- **Consommation publique en volume** : +1,3 %/an, rythme moyen 2011-2019.
- **Zone euro** : croissance et inflation du FMI. La demande adressée vaut 1,5 × la croissance de la zone euro
  (hypothèse D). Les prix d'importation suivent l'inflation de la zone euro.
- **Taux de l'OAT à 10 ans** : maintenu à 4,89 % (octobre 2026, Eurostat `irt_lt_mcby_m`). Le taux apparent de la dette
  le rejoint au rythme de 1/8 par an.
- **Chômage structurel** : 7,5 %.

## 3. Résultat (novembre 2026)

| | 2025 (obs.) | 2026 | 2028 | 2030 | 2032 |
|---|---|---|---|---|---|
| Croissance (%) | 0,8 | 0,3 | 1,2 | 1,1 | 1,2 |
| Chômage (%) | 7,5 | 8,1 | 7,6 | 7,3 | 7,0 |
| Solde public (% du PIB) | −5,1 | −5,4 | −6,6 | −7,6 | −8,5 |
| Dette publique (% du PIB) | 115,7 | 117,7 | 123,7 | 131,7 | 141,4 |
| Charge d'intérêts (% du PIB) | 2,5 | 2,9 | 3,6 | 4,4 | 5,1 |
| Pensions de droit direct (% du PIB) | 13,4 | 13,3 | 13,7 | 14,0 | 14,3 |
| Retraités pour 100 actifs | 54 | 53 | 54 | 55 | 56 |
| Industrie manufacturière (% du PIB) | 9,6 | 9,4 | 9,0 | 8,6 | 8,2 |

**Comparaison avec le FMI.** Le FMI projette un solde de −3,9 % et une dette de 124 % du PIB en 2031. Ces projections
supposent un redressement budgétaire non encore voté. La différence avec cette trajectoire, environ 4 points de PIB de
solde en 2031, mesure l'effort que ce redressement représenterait.

**Comparaison avec le COR.** Le COR estime les dépenses de retraite à 14,1 % du PIB en 2025, stables jusqu'en 2045 ;
son champ inclut les pensions de réversion et tous les régimes. Ici, les pensions de droit direct passent de 13,4 % à
14,3 % du PIB d'ici 2032. Elles progressent plus vite que chez le COR parce que la croissance des salaires est plus
faible à court terme.

## 4. Limites et incertitudes

- **Taux d'intérêt.** Le taux de l'OAT est figé au niveau d'octobre 2026, alors que la prime sur le Bund est passée de
  70 à 170 points de base en un an. Chaque point de taux de marché en plus ou en moins représente environ 0,7 point de
  PIB de charge d'intérêts au bout de cinq ans.
- **Emploi industriel.** Il recule d'environ 1,8 % par an, ce qui est probablement trop rapide : le calage commun de
  l'emploi s'applique à toutes les branches.
- **Croissance après 2031.** Elle découle des hypothèses du COR, sans dynamique propre.
- **Dépenses publiques tendancielles.** Elles sont prolongées au rythme 2011-2019. C'est une convention : la loi de
  programmation et les normes de dépense ne sont pas intégrées.
- **Mesures en euros.** Elles sont exprimées en euros de 2025 et indexées sur le PIB nominal de la référence.

## Version 0.5 (audit de novembre 2026) : cible de taux d'épargne

Au-delà de 2025, la consommation des ménages n'absorbe plus l'écart de croissance au FMI : elle est calée sur une cible
de taux d'épargne (`taux_epargne_cible` : 17,9 % en 2025, 17,3 % en 2027, 15,5 % en 2031 et au-delà). L'écart de
croissance est comblé par l'investissement et les exportations. Sans cette cible, le taux d'épargne tombait à 11 % en
2032. Voir 12_audit_mecanismes.md, sections 3.8 et 4.8.
