# Robustesse, incertitudes et scénarios alternatifs {#sec:robustesse}

Ce chapitre rassemble les analyses de sensibilité : sur des stratégies de test standardisées (S1 à S5) et sur les
programmes eux-mêmes, sous dix régimes de politique économique, trois environnements alternatifs et des variantes de
paramètres structurels. Il distingue les types d'incertitude et indique ce qui est robuste et ce qui ne l'est pas.

## Typologie des incertitudes {#sec:typologie-incertitudes}

| Type | Définition | Traitement dans l'étude |
|---|---|---|
| **Statistique** | précision des paramètres estimés (écarts types) | intervalles disponibles pour les paramètres [E] ; non propagés systématiquement (le module M12 permet des tirages) |
| **Paramétrique** | valeur des paramètres calibrés ou non identifiés | variantes basse / haute de 17 paramètres structurels ; jeux « ancrage », « fermeture » ; environnements $\sigma$ et prix |
| **Structurelle** | forme des équations et des mécanismes (fermeture, anticipations, politique monétaire) | dix régimes ; comparaison avec les familles de modèles (chapitre \ref{sec:theorie}) ; mécanismes manquants (annexe \ref{sec:annexe-h}) |
| **Chocs futurs** | environnement international, prix de l'énergie, taux | variante de taux longs (OAT 3,82 % / 4,89 %) ; chocs du régime monétaire (non utilisés dans les résultats de base) |
| **Mise en œuvre** | ampleur et calendrier effectifs des mesures | variantes 50 % et retard de deux ans |
| **Politique et institutionnelle** | réactions européennes, contentieux, crédibilité | variantes « conforme », « contentieux », « tension » |

## Stratégies de test S1 à S5 sous dix régimes {#sec:s1s5}

Les cinq stratégies de test (S1 « protection », S2 « emploi », S3 « productivité », S4 « redressement », S5
« global ») sont des combinaisons de curseurs conçues lors des phases antérieures pour couvrir des orientations
contrastées ; elles servent de banc d'essai de la robustesse du modèle, indépendamment des programmes.

{{inc:t12_S}}

{{inc:t12_classements}}

**Constats.** (1) Les signes des effets sur le PIB et la dette sont identiques dans les dix régimes pour les cinq
stratégies, aux horizons de 10 et 20 ans. (2) Les classements extrêmes sont stables : S3 a toujours l'effet le plus
favorable sur le PIB et le plus défavorable sur la dette, S4 l'inverse. (3) L'ordre de S1 et S5 en PIB change selon le
régime. (4) Les effets sur l'emploi et le chômage changent de signe dans 11 cas sur 40 : régime actif symétrique,
variantes de fermeture et environnements $\sigma$ en sont les principales causes.

## Pourquoi le PIB et la dette sont plus robustes que l'emploi et le chômage — et quand ce n'est pas le cas {#sec:pourquoi}

Pour les **stratégies de test S1-S5**, les simulations confirment que les résultats sur le PIB et la dette sont plus
robustes que ceux sur l'emploi et le chômage. Trois raisons l'expliquent :

1. **Le PIB est contraint par la demande à court terme et par le potentiel à long terme**, deux mécanismes communs à
   tous les régimes ; l'emploi dépend en plus du partage de l'ajustement entre emploi et productivité (élasticité de
   court terme, $\sigma$), qui varie selon l'environnement.
2. **Le chômage est un solde** entre deux grandeurs (population active et emploi) qui réagissent toutes deux aux
   mesures ; une petite différence relative sur chacune produit une grande différence sur le solde.
3. **La dette cumule les soldes** : ses écarts croissent avec le temps et dominent les variations des régimes, sauf
   quand le régime lui-même agit sur la dette (règle active, prime souveraine), auquel cas l'ampleur change mais pas le
   signe.

Pour les **programmes des candidats**, le constat est différent et doit être énoncé tel quel (tableau suivant). Les
signes des effets sur le **chômage** sont stables dans toutes les variantes, parce qu'ils sont dominés par les réformes
des retraites, qui modifient la population active dans le même sens quel que soit le régime ; leur *ampleur* reste peu
fiable. À l'inverse, certains effets sur le **PIB** et la **dette** changent de signe : l'effet de LFI sur le PIB à dix et
vingt ans (proche de zéro et encadré par des valeurs des deux signes), l'effet du RN sur la dette (petit à toutes les
échéances), l'effet d'Horizons sur la dette à vingt ans. La règle générale qui ressort des deux exercices est que **la
robustesse du signe dépend du rapport entre l'ampleur de l'effet et l'étendue des variantes**, plus que de la nature de
l'indicateur : un effet important est robuste, un effet proche de zéro ne l'est pas, quelle que soit la variable.

## Robustesse des résultats des programmes {#sec:robustesse-programmes}

{{inc:t12_candidats}}

Part des couples (candidat, horizon) dont le signe est robuste aux treize variantes, par indicateur : {{inc:t12_part}}.

## Paramètres structurels {#sec:robustesse-parametres}

Amplitude maximale de l'effet à 20 ans sur les stratégies S1-S5 quand un paramètre passe de sa valeur basse à sa valeur
haute (régime principal ; paramètres monétaires sous le régime BCE + prime) :

{{inc:t12_structurels}}

{{inc:t12_monetaires}}

Aucun paramètre structurel testé ne modifie le classement des stratégies en PIB ou en dette ; les paramètres de prime
souveraine sont les plus influents sur la dette des stratégies déficitaires.

## Environnements alternatifs {#sec:robustesse-env}

Les environnements $\sigma = 0{,}3$ et $\sigma = 0{,}6$ et l'équation de prix v0.9 ont chacun été calibrés sur les
mêmes cibles. Pour les stratégies de test, $\sigma$ modifie l'effet sur le PIB de moins de 0,05 point à 20 ans mais
l'emploi et la dette davantage (jusqu'à 7 points de dette) ; l'équation de prix modifie la dette de 2,6 points au plus.
Les résultats des programmes dans ces environnements figurent au chapitre \ref{sec:resultats}.

## Ce qui est robuste, ce qui est fragile {#sec:robuste-fragile}

**Résultats robustes (signe stable dans toutes les variantes, ampleur comparable).**
- Le sens des effets des réformes des retraites sur la population active, le PIB potentiel et le PIB à 10 et 20 ans.
- Le sens des effets des programmes sur la dette relativement à la référence, dans la lecture A, pour LFI (baisse) et
  pour Horizons jusqu'à dix ans (hausse) ; pas pour le RN, dont l'effet sur la dette est proche de zéro.
- Le sens des effets des programmes sur le chômage (dominés par la population active), mais pas leur ampleur.
- L'ordre de grandeur de l'effort budgétaire implicite des objectifs de déficit (lecture B), relativement aux mesures
  documentées, sous une hypothèse de taux donnée.

**Résultats fragiles (signe ou ampleur dépendant des hypothèses).**
- L'ampleur des effets sur le chômage à toutes les échéances ; leur signe pour les stratégies de test S1-S5.
- Les effets proches de zéro : PIB de LFI à dix et vingt ans, dette du RN, dette d'Horizons à vingt ans, pouvoir
  d'achat du RN et d'Horizons.
- Les effets de court terme des mesures de demande, qui dépendent des multiplicateurs (régime monétaire, fermeture).
- Les rendements nets des impôts sur le capital et les patrimoines (fourchette des réactions des contribuables).
- Tous les résultats à 20 ans qui dépendent de la dynamique de la dette (taux longs, prime souveraine).
- L'effet de l'investissement hors budget, dont l'additionnalité et le financement ne sont pas modélisés.
