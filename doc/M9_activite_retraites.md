# M9 — Activité des seniors et retraites (version 0.1)

**État : construit et testé sur l'historique, couplé au modèle bouclé M8 pour les variantes de règle d'âge.**
Ce n'est pas encore un modèle de régimes de retraite : la durée d'assurance, la décote et la surcote, les régimes
complémentaires et les droits familiaux ne sont pas représentés séparément.
Code : `src/m9_retraites.py`. Test : `tests/validation_M9.py`. Rapport : `resultats/validation_M9.md`.

## 1. Chaîne de calcul

**Démographie (M1).** Population par âge simple et sexe, Insee : estimations 1962-2025, puis projection centrale
2026-2070.

**Règle d'âge.** Âge d'ouverture des droits (AOD) par génération, sous trois législations :

| Génération | AOD, législation actuelle | Loi de 2023 sans suspension |
|---|---|---|
| 1955-1960 | 62 ans | 62 ans |
| 1961 | 62 ans et 1 mois (moyenne de l'année) | idem |
| 1962 | 62 ans et 6 mois | idem |
| 1963 | 62 ans et 9 mois | idem |
| 1964 | 62 ans et 9 mois | 63 ans |
| 1965 | 63 ans | 63 ans et 3 mois |
| … | +3 mois par génération | … |
| 1969 et après | 64 ans | 64 ans dès 1968 |

Législation actuelle : suspension de la réforme de 2023 par la loi de financement de la sécurité sociale (LFSS) pour 2026 ; 64 ans pour la génération 1969. Des variantes numériques (par exemple 65 ans) sont prévues.

**Taux d'activité de 55 à 74 ans.** Ils sont exprimés relativement à celui des 50-54 ans et dépendent de l'écart entre
l'âge et l'AOD de la génération :
- *Avant l'AOD* : sorties précoces (carrières longues, invalidité, chômage, inactivité) en rampe sur 5 ans, avec une tendance à la baisse.
- *Après l'AOD* : une part reste active, puis décroît exponentiellement.
- *Paramètre β* : part du profil qui se décale avec l'AOD. La part 1 − β reste attachée à l'âge 62 ans.

Estimation par moindres carrés non linéaires sur les taux d'activité par tranche quinquennale de l'enquête Emploi
(Eurostat `lfsa_argan`, 2003-2019), pondérés par la population par âge simple. Résultats :
- β = 0,78 pour les femmes et 0,75 pour les hommes ;
- erreur quadratique moyenne : 1,0 point (femmes) et 1,1 point (hommes) dans l'échantillon.

**Retraités de droit direct.** Part retraitée par âge, déduite du même profil :
- avant l'AOD, la moitié des sorties précoces sont des départs anticipés ;
- après l'AOD, 40 % des actifs cumulent emploi et retraite.

Calage du nombre total sur Eurostat `spr_pns_ben` en 2015. Le facteur de calage (1,06) reflète les retraités
résidant à l'étranger.

**Pensions.** Modèle par génération :
- pension à la liquidation = ν × moyenne des 25 dernières années de salaire moyen par tête, revalorisées sur les prix ;
- revalorisation ensuite au 1er janvier, sur l'indice des prix à la consommation hors tabac de l'année précédente (Insee).

ν est calé sur la masse des pensions de droit direct de 2015 (Eurostat `spr_exp_pens`). Les pensions de réversion
(42 Md€) ne sont pas modélisées.

**Lien avec M8.**
- Population active : évolution de M9 appliquée au niveau observé.
- Seniors supplémentaires en emploi : part estimée × actifs supplémentaires. Ils sont ajoutés à l'emploi, donc à la masse salariale, aux cotisations et au revenu.
- Écart de masse des pensions : ajouté aux prestations reçues par les ménages et versées par les administrations publiques.

## 2. Validation

- **Activité.** Hors échantillon (2020-2025, relèvement de l'AOD de 62 ans à 62 ans et 9 mois) :
  - 60-64 ans : écart de 0 à 3 points ;
  - 55-59 ans : surestimation de 1 à 2 points ;
  - 65-69 ans : surestimation de 2 à 3 points.
  L'enquête Emploi a connu une rupture de série en 2021.
- **Part des actifs supplémentaires de 60-64 ans en emploi.** Le rapport Δ taux d'emploi / Δ taux d'activité vaut 0,89 sur 2010-2019. Neuf seniors maintenus actifs sur dix étaient en emploi.
- **Retraités et pensions** (calage en 2015 seulement) :
  - 2008-2022 : masse reproduite à ±2,3 %, effectifs à ±2 % ;
  - 2024 (données provisoires) : masse surestimée de 4,4 % et effectifs de 1,5 %. Deux causes probables : la sous-revalorisation des retraites complémentaires (Agirc-Arrco) et le report d'âge de 2023, encore mal capté.
- **Comparaison externe.** Insee (variante de projection de population active, 2023) : la réforme de 2023 rehausse la population active d'environ 600 000 personnes à l'horizon 2070, avec un écart maximal d'environ 800 000 au début des années 2030. M9 donne −980 000 actifs en 2035 pour un retour à 62 ans. C'est le même ordre de grandeur, environ 20 % au-dessus, alors que l'Insee intègre aussi la durée d'assurance et les carrières longues.
- **Coût de la suspension.** M9 l'évalue à 1,0 Md€ de pensions en 2027. Les estimations publiques citées dans la presse donnent environ 1,4 Md€.

## 3. Variantes (modèle bouclé, base 2022, écarts à la législation actuelle)

Résultats en 2035 :

| Variante | Actifs | Emploi | Pensions | PIB, modèle de demande | PIB, borne offre | Solde public, modèle | Solde, borne offre |
|---|---|---|---|---|---|---|---|
| Retour à 62 ans | −983 000 | −820 000 | +38 Md€ | +0,15 % | −2,5 % | −1,8 pt | −3,2 pt |
| Loi de 2023 sans suspension | +32 000 | +18 000 | −2,2 Md€ | ≈ 0 | +0,06 % | +0,1 pt | +0,1 pt |
| 65 ans | +367 000 | +330 000 | −5,9 Md€ | +0,06 % | +1,0 % | +0,5 pt | +1,0 pt |

**Lecture.** Les effets sur les pensions et les cotisations sont robustes : ils reposent sur la démographie, les règles
et des comportements d'activité bien reproduits.

L'effet sur le PIB dépend de la fermeture du modèle :
- Dans M8, la production est déterminée par la demande. Les seniors maintenus en emploi touchent un salaire mais ne produisent rien de plus. Un retour à 62 ans y paraît même légèrement favorable à court terme : les pensions versées dépassent les salaires perdus.
- À long terme, la production suit l'emploi disponible : c'est la « borne offre ».

Ces deux colonnes encadrent l'effet. Il manque une fermeture d'offre dans M8 (production potentielle, taux d'utilisation
des capacités) pour trancher (décision A11).

## 4. Limites

- Pas de durée d'assurance, de décote ni de surcote, ni de distinction entre régimes ; les retraites complémentaires sont indexées comme les régimes de base ; pas de réversion.
- Taux d'activité avant 55 ans maintenus à leur dernier niveau observé ; tendance des sorties précoces gelée après 2025.
- Prix et salaires utilisés pour les pensions futures : conventionnels, non bouclés avec M8.
- Pas de solde du système de retraite au sens du Conseil d'orientation des retraites (COR) : les pensions et les cotisations sont incluses dans le compte des administrations publiques de M8.
