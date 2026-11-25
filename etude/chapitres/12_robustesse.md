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

**Tableau : stratégies de test S1-S5 sous les dix régimes** (principal, minimum, maximum, stabilité du signe). Source : phase5/resultats/lot53_synthese_S1_S5.csv.

| stratégie — horizon — indicateur | principal | min | max | signe robuste |
|---|---|---|---|---|
| S1_protection — 10 ans — PIB (%) | +1,00 | +0,32 | +1,49 | oui |
| S1_protection — 10 ans — emploi (milliers) | +420,65 | +222,34 | +531,10 | oui |
| S1_protection — 10 ans — chômage (pt) | −0,70 | −1,02 | −0,12 | oui |
| S1_protection — 10 ans — dette (pt PIB) | +3,64 | +0,58 | +5,32 | oui |
| S1_protection — 20 ans — PIB (%) | +0,32 | +0,10 | +0,78 | oui |
| S1_protection — 20 ans — emploi (milliers) | +178,68 | +65,56 | +295,64 | oui |
| S1_protection — 20 ans — chômage (pt) | +0,01 | −0,34 | +0,34 | non |
| S1_protection — 20 ans — dette (pt PIB) | +16,92 | +9,31 | +23,43 | oui |
| S2_emploi — 10 ans — PIB (%) | +1,48 | +1,14 | +1,66 | oui |
| S2_emploi — 10 ans — emploi (milliers) | +203,63 | +136,59 | +251,75 | oui |
| S2_emploi — 10 ans — chômage (pt) | −0,15 | −0,29 | +0,05 | non |
| S2_emploi — 10 ans — dette (pt PIB) | +8,43 | +7,34 | +9,65 | oui |
| S2_emploi — 20 ans — PIB (%) | +2,39 | +1,89 | +2,93 | oui |
| S2_emploi — 20 ans — emploi (milliers) | +102,73 | −28,24 | +300,54 | non |
| S2_emploi — 20 ans — chômage (pt) | +0,15 | −0,44 | +0,53 | non |
| S2_emploi — 20 ans — dette (pt PIB) | +24,22 | +22,28 | +32,06 | oui |
| S3_productivite — 10 ans — PIB (%) | +2,76 | +2,22 | +3,25 | oui |
| S3_productivite — 10 ans — emploi (milliers) | +458,22 | +346,55 | +531,84 | oui |
| S3_productivite — 10 ans — chômage (pt) | +0,74 | +0,53 | +1,06 | oui |
| S3_productivite — 10 ans — dette (pt PIB) | +14,14 | +12,93 | +16,34 | oui |
| S3_productivite — 20 ans — PIB (%) | +5,19 | +4,53 | +6,66 | oui |
| S3_productivite — 20 ans — emploi (milliers) | +758,84 | +581,10 | +1293,94 | oui |
| S3_productivite — 20 ans — chômage (pt) | +1,38 | −0,14 | +1,90 | non |
| S3_productivite — 20 ans — dette (pt PIB) | +37,75 | +33,20 | +52,36 | oui |
| S4_redressement — 10 ans — PIB (%) | −0,79 | −0,93 | −0,45 | oui |
| S4_redressement — 10 ans — emploi (milliers) | −69,03 | −100,12 | +44,16 | non |
| S4_redressement — 10 ans — chômage (pt) | +0,20 | −0,13 | +0,29 | non |
| S4_redressement — 10 ans — dette (pt PIB) | −16,58 | −17,55 | −15,30 | oui |
| S4_redressement — 20 ans — PIB (%) | −1,00 | −1,43 | −0,38 | oui |
| S4_redressement — 20 ans — emploi (milliers) | −14,00 | −120,72 | +133,77 | non |
| S4_redressement — 20 ans — chômage (pt) | +0,04 | −0,40 | +0,36 | non |
| S4_redressement — 20 ans — dette (pt PIB) | −38,54 | −44,07 | −35,49 | oui |
| S5_global — 10 ans — PIB (%) | +0,64 | +0,57 | +0,94 | oui |
| S5_global — 10 ans — emploi (milliers) | −47,89 | −61,37 | +56,40 | non |
| S5_global — 10 ans — chômage (pt) | +0,47 | +0,16 | +0,51 | oui |
| S5_global — 10 ans — dette (pt PIB) | +3,22 | +2,35 | +4,92 | oui |
| S5_global — 20 ans — PIB (%) | +1,33 | +1,12 | +1,56 | oui |
| S5_global — 20 ans — emploi (milliers) | −92,05 | −141,64 | +57,93 | non |
| S5_global — 20 ans — chômage (pt) | +0,60 | +0,16 | +0,75 | oui |
| S5_global — 20 ans — dette (pt PIB) | +11,17 | +7,65 | +18,07 | oui |

**Tableau : classements des stratégies S1-S5 par régime** (du plus favorable au moins favorable). Source : phase5/resultats/lot53_classements_S1_S5.csv.

| régime                                      | ('PIB (%)', '10')      | ('PIB (%)', '20')      | ('chômage (pt)', '10')   | ('chômage (pt)', '20')   | ('dette (pt PIB)', '10')   | ('dette (pt PIB)', '20')   | ('prix (%)', '10')     | ('prix (%)', '20')     |
|:--------------------------------------------|:-----------------------|:-----------------------|:-------------------------|:-------------------------|:---------------------------|:---------------------------|:-----------------------|:-----------------------|
| R2 + BCE et prime                           | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S4 > S1 > S2 > S5 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| R2 active symétrique                        | S3 > S2 > S5 > S1 > S4 | S3 > S2 > S5 > S1 > S4 | S4 > S1 > S2 > S5 > S3   | S2 > S3 > S5 > S1 > S4   | S4 > S1 > S5 > S2 > S3     | S4 > S1 > S5 > S2 > S3     | S5 > S3 > S2 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| R2, ancrage faible                          | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S4 > S1 > S2 > S5 > S3   | S4 > S1 > S5 > S2 > S3     | S4 > S1 > S5 > S2 > S3     | S5 > S3 > S2 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| R2, ancrage fort                            | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S1 > S4 > S2 > S5 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S5 > S3 > S2 > S1 > S4 |
| R2, fermeture lente                         | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S1 > S4 > S2 > S5 > S3   | S4 > S1 > S5 > S2 > S3     | S4 > S1 > S5 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| R2, fermeture rapide                        | S3 > S2 > S5 > S1 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S4 > S2 > S1 > S5 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| R2, fermeture sur le chômage                | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S4 > S2 > S5 > S3   | S4 > S1 > S5 > S2 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S3 > S2 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| principal (R2 figé, taux exogènes, central) | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S1 > S4 > S2 > S5 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| sans règle budgétaire (R0)                  | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S1 > S4 > S2 > S5 > S3   | S4 > S1 > S5 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S3 > S2 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |
| stabilisation (R1)                          | S3 > S2 > S1 > S5 > S4 | S3 > S2 > S5 > S1 > S4 | S1 > S2 > S4 > S5 > S3   | S1 > S4 > S2 > S5 > S3   | S4 > S5 > S1 > S2 > S3     | S4 > S5 > S1 > S2 > S3     | S5 > S2 > S3 > S4 > S1 | S3 > S5 > S2 > S4 > S1 |

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

**Tableau : robustesse de la lecture A des programmes aux dix régimes et aux trois environnements alternatifs** (signe identique dans les 13 variantes ; étendue max − min). Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py.

| candidat — indicateur | signe robuste à 5 ans | signe robuste à 10 ans | signe robuste à 20 ans | étendue à 5 ans | étendue à 10 ans | étendue à 20 ans |
|---|---|---|---|---|---|---|
| Le Pen (RN) — PIB (%) | oui | oui | oui | +0,76 | +0,72 | +1,30 |
| Le Pen (RN) — chômage (pt) | oui | oui | oui | +0,39 | +0,49 | +1,24 |
| Le Pen (RN) — dette (pt PIB) | non | non | non | +2,01 | +6,95 | +22,59 |
| Le Pen (RN) — emploi (milliers) | oui | oui | oui | +127,92 | +157,84 | +400,68 |
| Le Pen (RN) — pouvoir d'achat (%) | oui | non | non | +0,37 | +1,22 | +3,89 |
| Le Pen (RN) — solde (pt PIB) | oui | non | non | +0,42 | +0,80 | +2,08 |
| Mélenchon (LFI) — PIB (%) | oui | non | non | +1,88 | +2,38 | +2,53 |
| Mélenchon (LFI) — chômage (pt) | oui | oui | oui | +0,88 | +1,70 | +2,09 |
| Mélenchon (LFI) — dette (pt PIB) | oui | oui | oui | +10,22 | +29,10 | +70,76 |
| Mélenchon (LFI) — emploi (milliers) | oui | non | oui | +290,01 | +560,03 | +681,77 |
| Mélenchon (LFI) — pouvoir d'achat (%) | oui | oui | oui | +1,38 | +3,70 | +6,26 |
| Mélenchon (LFI) — solde (pt PIB) | oui | oui | oui | +1,56 | +3,19 | +6,03 |
| Philippe (Horizons) — PIB (%) | oui | oui | oui | +1,90 | +2,80 | +2,58 |
| Philippe (Horizons) — chômage (pt) | oui | oui | oui | +1,34 | +2,37 | +2,63 |
| Philippe (Horizons) — dette (pt PIB) | oui | oui | non | +4,10 | +13,57 | +44,26 |
| Philippe (Horizons) — emploi (milliers) | oui | non | non | +458,15 | +820,85 | +913,36 |
| Philippe (Horizons) — pouvoir d'achat (%) | non | non | non | +2,26 | +5,76 | +9,44 |
| Philippe (Horizons) — solde (pt PIB) | oui | oui | non | +0,82 | +2,04 | +4,17 |

Part des couples (candidat, horizon) dont le signe est robuste aux treize variantes, par indicateur : PIB (%) : 78 % ; chômage (pt) : 100 % ; dette (pt PIB) : 56 % ; emploi (milliers) : 67 % ; pouvoir d'achat (%) : 44 % ; solde (pt PIB) : 67 %.

## Paramètres structurels {#sec:robustesse-parametres}

Amplitude maximale de l'effet à 20 ans sur les stratégies S1-S5 quand un paramètre passe de sa valeur basse à sa valeur
haute (régime principal ; paramètres monétaires sous le régime BCE + prime) :

| paramètre | amplitude PIB 20 ans (pt de %) | amplitude dette 20 ans (pt) |
|---|---|---|
| PSI_CHOMAGE | 0,02 | 0,55 |
| PSI_TAUX | 0,02 | 0,14 |
| SEMI_ELAST_IS | 0,00 | 1,29 |
| THETA_TRESORERIE | 0,01 | 0,73 |
| bund_transmission | 0,00 | 0,00 |
| div_lissage | 0,01 | 1,41 |
| mu_taux | 0,00 | 0,02 |
| prime_dette | 0,00 | 0,00 |

| paramètre | amplitude PIB 20 ans (pt de %) | amplitude dette 20 ans (pt) |
|---|---|---|
| bce_activite | 0,13 | 6,47 |
| bce_inflation | 0,00 | 0,27 |
| bund_transmission | 0,00 | 2,32 |
| entreprises_vitesse | 0,08 | 0,69 |
| menages_vitesse | 0,00 | 0,13 |
| prime_dette | 0,02 | 7,09 |
| prime_solde | 0,01 | 7,63 |

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
