# Audit des mécanismes économiques et des effets de transmission (version 0.5, 17-18 novembre 2026)

Objet : vérifier que le modèle représente correctement les mécanismes de transmission entre agents, branches et reste
du monde ; corriger ce qui est mal représenté ; documenter ce qui manque. Démarche : cartographie du code existant,
recherche documentaire, tests de canaux par neutralisation, corrections hiérarchisées, nouvelle validation.

Niveaux de preuve utilisés : **E** paramètre estimé économétriquement sur données françaises ; **C** calibré sur une
source empirique ; **H** hypothèse de modélisation ; **R** relation comptable ; **T** relation théorique non validée
directement.

## 1. Cartographie des mécanismes (état avant audit, version 0.4.1)

| Mécanisme | Où | Représentation | Calibrage, preuve | Limites constatées |
|---|---|---|---|---|
| Consommation des ménages | m7_equations.consommation, m8 `simuler` §4 | MCE : Δln C = a + 0,85 Δln RDB réel − 0,22 (ln C − ln RDB réel)₋₁ | E (1997-2019) ; élasticité de long terme 1 imposée | Une seule propension pour tous les ménages et tous les revenus ; pas d'effet de richesse, de taux d'intérêt ni de précaution (retiré en v0.5, biais de simultanéité) |
| Épargne des ménages | implicite | résidu RDB − consommation | R | Destination de l'épargne non représentée ; pas de patrimoine |
| Investissement logement des ménages | m8, FBCF « autres » | **exogène** (indice `autres_investissements`) | — | Ne réagit ni au revenu ni aux taux |
| Contenu importé de la demande | m5 + m8 `_leontief` | tableau entrées-sorties 2022 (Eurostat FIGARO / Insee) : parts importées par produit et par emploi final, consommations intermédiaires importées ; facteur commun φ ajusté pour respecter l'équation agrégée d'importations | R + E | φ s'appliquait aussi à l'énergie : substitution fictive vers la production nationale en cas de hausse du prix de l'énergie importée |
| Valeur ajoutée nationale des produits importés (commerce, transport) | m8 `_leontief` | marges de commerce et de transport comptées comme produits des branches G et H (tableau aux prix de base) | R | Correct |
| Équation d'importations | m7_equations.importations | MCE sur la demande pondérée par le contenu importé et le prix relatif | E | Prix relatif calculé avec l'énergie (voir ci-dessus) ; tension des capacités non significative (testée) |
| Exportations | m7_equations.exportations | différences : demande de l'UE, prix relatif | E | Pas de relation de long terme identifiée ; pas de change hors zone euro |
| Investissement des entreprises | m7 investissement, investissement_snf | accélérateur par branche (MCE) + coût d'usage du capital (taux, IS, prix relatif) | E | Profits non distribués et dividendes non représentés ; pas d'effet de trésorerie |
| Distribution des profits | m8 `_revenus_patrimoine` | revenus de la propriété des ménages ∝ PIB nominal | H | Une baisse d'IS n'augmente pas les dividendes ; aucun revenu versé aux non-résidents |
| Revenu national | — | absent | — | PIB seulement ; pas de RNB ni de solde extérieur |
| Salaires | m7 salaires | MCE sur la part des salaires, indexation sur les prix, courbe de Phillips calibrée (−0,4 % par point de chômage) | E + C | — |
| Prix de valeur ajoutée | m7 prix_va | MCE sur le coût salarial unitaire, tension des capacités (industrie) | E | Ne capte pas les prix de marché de l'électricité ni les reconstitutions de marges (2023) |
| Prix d'importation → prix intérieurs | m7 transmission, m8 θ | ajustement partiel θ = 0,50 par an | E (1998-2024) | — |
| Capacités de production | m8 `_tuc`, réindustrialisation | taux d'utilisation des capacités (industrie) dans les prix ; capital installé | E + H | Réindustrialisation : capacités supposées produire la même année que l'investissement |
| Contrainte d'offre globale | m8 fermeture d'offre | correcteur proportionnel-intégral ramenant le chômage vers le chômage structurel (politique monétaire, crédit, compétitivité) | H | Mécanisme réduit, symétrique |
| Finances publiques | m8 `_finances` | taux apparents, IS sur l'EBE marchand, intérêts au taux apparent convergeant vers l'OAT | R + C | — |
| Effets d'offre de l'investissement public | simulateur/executer | élasticité de la production au capital public 0,08 | C (Bom et Ligthart 2014) | — |
| Comptes financiers, bilans | — | dette publique seulement | — | Pas de cadre stock-flux complet |
| Europe | m11 | BCE, taux longs, demande des partenaires | C | — |
| Comportements des hauts revenus | m13 | élasticités du revenu imposable, mobilité | C | — |

## 2. Recherche documentaire et données

- **Propensions à consommer par niveau de vie.** Insee Focus n° 338 (2024) : en 2022, taux d'épargne de −29 %
  (quintile 1), 0, 6, 10 et 27 % (quintile 5) ; structures de consommation par quintile. Garbinti et Lamarche (2014) :
  taux d'épargne croissant avec le revenu permanent. Insee, Note de conjoncture de juin 2019 : +1 % de revenu → +0,5 %
  de consommation après un an, +0,8 % à long terme, par fonction de consommation ; pas d'équation estimable par
  catégorie de ménages (données trimestrielles absentes). Banque de France (Arrondel, Lamarche, Savignac 2015 ;
  Garbinti et al., document de travail n° 751) : propension à consommer la richesse décroissante le long de la
  distribution.
- **Destination de l'épargne** (Eurostat nasa_10_f_tr, comptes financiers, flux nets 2022 / 2024, Md€) : dépôts
  +87 / +30 ; titres de dette +7 / +5 ; actions +33 / +27 ; fonds +12 / +32 ; assurance-vie et retraite +37 / +59 ;
  crédits nouveaux nets (passif) +84 / +3. Épargne brute 284 / 351 ; investissement (logement surtout) 176 / 155.
  Banque de France : flux nets de placements 128 Md€ en 2025, surtout assurance-vie et droits à pension.
- **Profits et dividendes** (Eurostat nasa_10_nf_tr, SNF, 2022) : excédent brut 420 Md€, IS 69 Md€, dividendes
  versés 273 Md€ (dont intra-groupes), reçus 220 Md€, FBCF 312 Md€, épargne brute 278 Md€. Ménages : dividendes reçus
  64 Md€. Banque de France (Bulletin 261/3, 2025) : 50 % du capital des sociétés françaises du CAC 40 détenu par des
  non-résidents en 2024. France Stratégie (comité d'évaluation des réformes de la fiscalité du capital, 2019-2023) :
  forte hausse des dividendes après 2018, effet sur l'investissement non démontré ; la littérature conclut à un effet
  négatif significatif du taux d'IS sur l'investissement, d'ampleur discutée.
- **Revenus primaires du reste du monde** (Eurostat) : RNB supérieur au PIB de 3,1 % en 2022 ; revenus de la propriété
  reçus du reste du monde 217 Md€, versés 165 Md€.
- **Subventions sur les produits** (Eurostat nama_10_gdp, D31) : 15 Md€ en 2021, 37 Md€ en 2022, 33 Md€ en 2023,
  18 Md€ en 2024 (bouclier tarifaire).

## 3. Tests effectués et résultats de l'audit

Les résultats chiffrés figurent en section 5 (variantes avant / après) ; cette section donne les diagnostics.

### 3.1 Salaires +2 % : pourquoi l'emploi baisse

Décomposition par neutralisation des canaux (outputs/audit_variantes_avant.md, 2030) :
- effet direct (consommation et boucle prix-salaires neutralisées) : emploi −57 000 ; le coût salarial unitaire
  augmente, l'emploi de chaque branche s'ajuste à la baisse (substitution capital-travail, élasticité estimée), les
  prix de valeur ajoutée montent (+1,1 % pour les prix à la consommation), les exportations reculent (−0,5 %) ;
- revenus et consommation : le revenu disponible réel augmente, la consommation +0,4 %, l'emploi remonte à −23 000 ;
- boucle prix-salaires : l'indexation propage la hausse (salaires +2,4 % en 2030), compétitivité −0,6 % à l'export ;
- au total, PIB −0,03 %, emploi −27 000, solde public +0,2 point (cotisations et impôts sur une masse salariale plus
  élevée).
Verdict : le résultat est cohérent avec les mécanismes représentés et avec la littérature française (la hausse du coût
du travail réduit la demande de travail et la compétitivité ; le gain de pouvoir d'achat compense en partie). Il est
dépendant de l'élasticité de substitution capital-travail (estimée) et de l'absence d'hétérogénéité des propensions
(une hausse des bas salaires aurait un effet de demande plus fort : traité en 4.2).

### 3.2 Énergie importée : substitution fictive (anomalie)

Avec le facteur commun d'importation figé, le choc de +50 % sur l'énergie importée coûtait −1,40 % de PIB en 2030 ;
avec le modèle complet, seulement −0,43 %. L'écart venait de deux défauts : le prix relatif des importations incluait
l'énergie (une hausse du prix du pétrole « rendait » les importations moins compétitives), et le facteur φ abaissait
les parts importées de tous les produits, y compris industriels. Corrigé en 4.1.

### 3.3 Impôt sur les sociétés : investissement seulement

La baisse de l'IS passe uniquement par le coût d'usage du capital (FBCF +1,6 % en 2030, PIB +0,17 %), sans
distribution de dividendes, sans revenus versés aux non-résidents. Le multiplicateur budgétaire est faible, ce qui est
cohérent avec France Stratégie, mais la destination du supplément de profit n'était pas représentée. Corrigé en 4.3.

### 3.4 Contenu importé selon le niveau de vie (testé, non retenu)

Contenu en importations (direct et indirect, tableau entrées-sorties 2022) par fonction de consommation, pondéré par les
structures de consommation par quintile de l'Insee (2022) : 31,1 % (quintile 1), 32,0 %, 32,3 %, 32,1 %, 32,3 %
(quintile 5). L'écart est d'environ un point : le logement (peu importé) pèse plus chez les modestes, les loisirs et
l'équipement (plus importés) chez les aisés. L'effet sur le PIB d'une redistribution est inférieur à 0,01 point par
milliard ; il n'est pas modélisé. L'hétérogénéité pertinente est celle de l'épargne (4.2), non celle des importations.
Limite : à l'intérieur d'une fonction (marques, gammes), les données ouvertes ne permettent pas de distinguer.

### 3.5 Tension des capacités et importations (testé, non retenu)

Ajout du taux d'utilisation des capacités de l'industrie à l'équation d'importations (1997-2019) : coefficient −0,002
(t = −1,7, mauvais signe) en niveau, non significatif en variation. Le débordement de la demande vers les importations
passe par l'élasticité de court terme à la demande (1,47), déjà élevée.

### 3.6 Taux d'intérêt et logement (testé, non retenu)

Investissement des ménages en logement (Eurostat, 1997-2019 et 1997-2024) : le taux long (niveau ou variation) n'est
pas significatif et a le mauvais signe. Le canal du crédit immobilier (forte baisse des crédits nouveaux en 2023-2024)
n'est pas identifié sur données annuelles agrégées ; le revenu l'est (élasticité 1,5, t = 1,5 ; rappel −0,28).

### 3.7 Inflation de 2023 (diagnostic)

Rétrosimulation base 2022 : prix de la consommation +4,3 % simulé en 2023 contre +7,1 % observé (déflateur de la
consommation). Le paramètre θ n'explique pas l'écart (θ de 0,3 à 0,6 : 4,0 %). Les prix de valeur ajoutée observés en
2023 montrent l'origine : électricité et gaz (branche D) +114 %, industries agroalimentaires +30 %, commerce +8,9 %
pour des coûts salariaux unitaires de −23 %, +18 % et +6,9 %. Ces hausses viennent des prix de marché européens de
l'électricité (production nationale vendue au prix de marché, non au coût) et de la reconstitution des marges, que
l'équation de prix fondée sur le coût salarial unitaire ne représente pas. Contribution approchée au déflateur du PIB :
environ 1,5 point sur 5,1. Le bouclier tarifaire n'explique pas 2023 (subventions sur les produits presque inchangées
entre 2022 et 2023 : 37 et 33 Md€) mais contribue à 2024 (18 Md€).
Correction non faite : il faudrait des prix de production de l'énergie par produit, non disponibles dans les tableaux
utilisés au-delà de l'année de base ; mécanisme documenté comme absent (section 6).

### 3.8 Trajectoire de référence : taux d'épargne (anomalie)

Le nouvel indicateur de taux d'épargne a révélé une incohérence de la trajectoire « politique inchangée » des versions
0.3 et 0.4 : de 2026 à 2032, l'écart entre la croissance simulée et la croissance du FMI était comblé chaque année par
un supplément de consommation et d'investissement. La consommation progressait de 2 à 2,4 % par an en volume pour un
PIB à 1,1 %, et le taux d'épargne des ménages tombait de 17,9 % (2025) à 11,2 % (2032), niveau jamais observé. Aucune
source ne soutient cette hypothèse : le projet de loi de finances pour 2027 retient 17,3 % en 2027 et la Banque de
France une baisse lente. Corrigé en 4.8.

## 4. Corrections et ajouts (version 0.5)

### 4.1 Importations non concurrentes (énergie) — R + H
Houille, pétrole et gaz bruts (CPA_B), produits raffinés (C19), électricité et gaz (D) : leurs parts importées ne
s'ajustent pas au facteur commun φ ; leur prix est exclu du prix relatif de l'équation d'importations
(`m8_modele.NON_CONCURRENTS`). Traitement standard des importations non concurrentes dans les modèles entrées-sorties.

### 4.2 Propensions à consommer par décile — C
`m14_heterogeneite.py` : le revenu pris en compte par l'équation de consommation est corrigé du profil des propensions
par décile appliqué aux gains et pertes de la microsimulation (M10). Profil central de première année : 0,90 (décile 1)
à 0,40 (décile 10), 0,25 pour le dernier centile ; variantes « plat » et « accentué ». La moyenne reste celle de
l'équation estimée. Hypothèse simulateur : `hypotheses.pmc`.

Sensibilité (PIB en 2030, écart à la référence) : RSA +25 % : +0,08 % (profil plat, situation avant l'audit), +0,12 %
(central), +0,14 % (accentué) ; impôt sur la fortune à 1 % : −0,09 %, −0,06 %, −0,05 %. Le profil modifie l'effet
d'activité des mesures redistributives d'environ un tiers ; il ne change pas leur signe. Effets sur les jeux de mesures
des candidats en 2032 : au plus 0,13 point de PIB (voir 11_coherence_et_programmes.md).

### 4.3 Distribution des profits et revenus versés au reste du monde — C
Pour les mesures qui augmentent les profits après impôt (IS, impôts de production) : 50 % du supplément est distribué
en dividendes en trois ans (30 à 70 %), dont 40 % aux non-résidents ; 35 % des dividendes versés aux résidents sont
reçus directement par les ménages (le reste par les sociétés financières et assureurs), avec la propension du dernier
centile. Le reste est conservé par les entreprises (autofinancement, trésorerie, désendettement) ; l'effet sur
l'investissement continue de passer par le coût d'usage du capital (estimé). Hypothèse simulateur :
`hypotheses.distribution_profits`.

### 4.4 Investissement des ménages en logement — E
Endogène (équation 4.6 ci-dessus) au lieu d'être exogène.

### 4.5 Réindustrialisation : délai de construction des capacités — H
Les capacités nouvelles produisent deux ans après le début de l'investissement (`DELAI_CAPACITES`) ; l'investissement
précède la substitution aux importations.

### 4.6 Comptes d'agents — R
Nouvelles sorties : RNB (PIB + revenus primaires nets du reste du monde, dividendes versés aux non-résidents déduits),
épargne et taux d'épargne des ménages, investissement des ménages, capacité de financement des ménages, solde
extérieur courant approché. Tests automatiques d'identités : `tests/test_m14_identites.py`.

### 4.8 Trajectoire de référence : cible de taux d'épargne — C + H
`m8_reference.taux_epargne_cible` : 17,9 % (2025, observé), 17,3 % en 2027 (projet de loi de finances), puis retour
linéaire à 15,5 % en 2031, entre ce niveau et la moyenne d'avant la crise sanitaire (environ 15 %). La consommation est
calée sur cette cible ; l'écart de croissance avec le FMI est comblé par l'investissement et les parts de marché à
l'exportation (hypothèse : la reprise prévue par le FMI et la Banque de France n'est pas financée par un effondrement de
l'épargne). Trajectoire obtenue : croissance conforme au FMI à 0,04 point près ; solde public −9,0 % du PIB en 2032 au
lieu de −8,5 % ; dette 141,7 % au lieu de 141 %. Effet sur les variantes : faible (les écarts à la référence dépendent
peu du niveau de la référence).

### 4.7 Corrections diverses
- FBCF « autres » : l'indice exogène (mesures d'investissement public, logements sociaux) s'applique au total de l'année
  de base ; la part des ménages, devenue endogène, est remplacée par sa valeur simulée (sans cette précaution, les
  mesures d'investissement public auraient perdu 60 % de leur montant).
- Transferts non ciblés aux ménages combinés à des mesures microsimulées : montants exprimés sur la même année de
  revenus (auparavant, l'indexation des deux types de mesures pouvait différer d'environ 6 %).

## 5. Les cinq variantes avant et après l'audit

Écarts à la trajectoire « politique inchangée », mesures en vigueur en 2028, modèle complet (fermeture d'offre
comprise). Détail par canal et par année : outputs/audit_variantes_avant.md et outputs/audit_variantes_apres.md
(script tests/audit_variantes.py).

| Variante | PIB 2030 avant | après | Emploi 2030 (milliers) avant | après | Solde public 2030 (pt) avant | après | Dette 2030 (pt) avant | après |
|---|---|---|---|---|---|---|---|---|
| 1. Salaires +2 % (choc ponctuel 2028) | −0,03 % | −0,03 % | −27 | −26 | +0,20 | +0,20 | −2,81 | −2,81 |
| 2. IS de 25,8 % à 20 % | +0,17 % | +0,19 % | +29 | +32 | −0,53 | −0,53 | +1,36 | +1,34 |
| 3. Consommation publique +1 pt de PIB | +0,76 % | +0,78 % | +240 | +244 | −0,35 | −0,34 | −0,51 | −0,55 |
| 4a. Réindustrialisation −20 % immédiate, sans coût (borne haute) | +1,06 % | +0,83 % | +126 | +108 | +0,66 | +0,64 | −6,89 | −6,89 |
| 4b. Réindustrialisation −20 % en 5 ans, investissement, surcoût 10 % | +1,33 % | +0,44 % | +172 | +62 | +0,35 | +0,11 | −2,09 | −0,64 |
| 5. Prix de l'énergie importée +50 % | −0,43 % | −1,21 % | −159 | −280 | −0,71 | −0,97 | +0,49 | +1,95 |

Les résultats « après » intègrent aussi la nouvelle trajectoire de référence (4.8). Les chiffres cités dans la demande (PIB +2,8 % pour la réindustrialisation, −0,4 % pour l'énergie, +1,15 % pour la
dépense publique) venaient de la version 0.1 ; les versions 0.2 à 0.4 avaient déjà réduit les multiplicateurs
(consommation sans effet du chômage, fermeture d'offre, calendrier 2028). L'audit modifie surtout l'énergie (effet
presque triplé, substitution fictive supprimée) et la réindustrialisation progressive (effet divisé par 3 en 2030 :
les capacités produisent après deux ans de construction).

Lecture par canal (2030, version 0.5) :
- **Salaires +2 %** : effet direct emploi −54 000 (coût du travail, compétitivité), revenus et consommation +35 000,
  boucle prix-salaires −5 000. Part de la demande supplémentaire servie par les importations supérieure à 1 : les
  importations augmentent aussi par le prix relatif (les prix français montent).
- **IS** : FBCF +1,7 %, l'essentiel du supplément de profit est conservé (autofinancement) ou distribué ; consommation
  +0,12 % seulement (dividendes concentrés, propension faible) ; RNB +7,5 Md€ en 2032 contre PIB nominal +10,5 Md€ :
  environ 3 Md€ de dividendes supplémentaires versés aux non-résidents.
- **Dépense publique** : multiplicateur 1,0 la première année (effet direct), 1,28 avec la consommation induite, 0,79
  après la fermeture d'offre (resserrement monétaire et financier, compétitivité-prix : exportations −0,2 %). Très peu
  d'importations directes (services publics).
- **Réindustrialisation** : la borne haute (substitution immédiate, sans investissement ni surcoût) reste une borne,
  non un scénario plausible. La version progressive tient compte du délai de construction, de l'investissement et du
  surcoût ; elle ne tient pas compte des contraintes de qualification ni d'énergie (section 6).
- **Énergie** : perte de revenu réel (prix à la consommation +4,4 %), consommation −2,8 %, emploi −280 000 ; la
  hausse des prix détériore le solde extérieur (−77 Md€ en 2030) et le revenu national.

## 6. Validation historique avant / après

Rétrosimulations du modèle bouclé (tests/validation_M8.py ; coefficients estimés sur la période précédant la
simulation ; seules les exogènes sont observées) :

| Erreur de niveau en fin de période | 2015-2019 avant | après | 2023-2024 avant | après |
|---|---|---|---|---|
| PIB en volume | −0,3 % | −0,2 % | −3,6 % | −4,0 % |
| Consommation des ménages | +1,6 % | +1,7 % | −1,6 % | −1,7 % |
| Investissement total | −0,2 % | −0,4 % | −3,8 % | −3,7 % |
| Importations | +5,0 % | +4,7 % | −2,5 % | −1,9 % |
| Prix à la consommation | +0,3 % | +0,5 % | −2,9 % | −2,9 % |
| Chômage (points) | +0,3 | +0,2 | +0,6 | +0,8 |
| Dette publique (points de PIB) | +1,7 | +1,0 | +2,3 | +2,8 |

Les corrections améliorent légèrement 2015-2019 et sont neutres à légèrement défavorables sur 2023-2024 ; cette
dernière période reste mal reproduite pour des raisons identifiées (exportations −10 %, inflation de 2023, chute de
l'investissement en logement liée au crédit, non expliquée par le revenu). Les tests d'identités comptables
(tests/test_m14_identites.py) et les validations M7, M8 et M9 passent.

## 7. Mécanismes absents ou insuffisants après l'audit (liste hiérarchisée)

1. **Prix de marché de l'énergie produite en France** (électricité, gaz) et reconstitution des marges : explique
   l'essentiel de l'écart d'inflation de 2023 ; nécessite des prix de production par produit au-delà de l'année de base
   (indices de prix de production Insee par produit, à intégrer).
2. **Crédit et taux d'intérêt pour les ménages** : non identifié sur données annuelles ; une estimation trimestrielle
   (crédits nouveaux à l'habitat, Banque de France) permettrait d'introduire l'effet des taux sur le logement.
3. **Cadre stock-flux complet** : seuls la dette publique et les flux d'agents (épargne, capacité de financement des
   ménages, solde extérieur, RNB) sont suivis ; les bilans des ménages et des sociétés, les comptes financiers et leurs
   effets de richesse ne sont pas représentés. Un cadre SFC complet (Godley et Lavoie) demanderait une refonte du bloc
   financier ; il serait surtout utile pour les scénarios de taux et de dette, moins pour les mesures budgétaires.
4. **Contraintes de main-d'œuvre par qualification** : la réindustrialisation et les créations d'emplois publics
   supposent un appariement sans friction, sauf par la courbe de Phillips agrégée.
5. **Destination de l'épargne et financement de l'industrie** : les placements des ménages (assurance-vie surtout) ne
   sont pas reliés au coût du financement des entreprises ; aucune mesure ciblant l'épargne (livret, fléchage) n'est
   donc simulable au-delà de son coût budgétaire.
6. **Change hors zone euro** : absent (prix mondiaux en euros exogènes).
7. **Propensions à consommer estimées sur données françaises de panel** : le profil par décile est calibré, non
   estimé.

## 8. Références

- Insee Focus n° 338 (novembre 2024), « Consommation et épargne par catégories de ménages en 2022 ».
- Insee, Note de conjoncture de juin 2019, dossier « Quel lien entre pouvoir d'achat et consommation des ménages ? ».
- Garbinti B., Lamarche P. (2014), « Les hauts revenus épargnent-ils davantage ? », Économie et Statistique n° 472-473.
- Arrondel L., Lamarche P., Savignac F. (2015), « Wealth effects on consumption across the wealth distribution »,
  Banque de France, document de travail n° 552 ; Garbinti B. et al., document de travail n° 751.
- Jappelli T., Pistaferri L. (2014), « Fiscal policy and MPC heterogeneity », American Economic Journal: Macroeconomics.
- Fagereng A., Holm M., Natvik G. (2021), « MPC heterogeneity and household balance sheets », AEJ: Macroeconomics.
- France Stratégie, Comité d'évaluation des réformes de la fiscalité du capital, rapports 2019 à 2023 ; Comité
  d'évaluation du plan France Relance (2024), chapitre « réduction des impôts de production ».
- Banque de France, Bulletin n° 261/3 (2025), détention des actions du CAC 40 par les non-résidents ; Stat Info
  « Épargne des ménages » (2025).
- Bom P., Ligthart J. (2014), « What have we learned from three decades of research on the productivity of public
  capital? », Journal of Economic Surveys.
- Eurostat : nasa_10_nf_tr, nasa_10_f_tr, nama_10_gdp (comptes non financiers et financiers des secteurs, impôts et
  subventions sur les produits) ; tableaux entrées-sorties de l'année 2022.
- Godley W., Lavoie M. (2007), Monetary Economics: An Integrated Approach to Credit, Money, Income, Production and
  Wealth (cadre stock-flux cohérent, référence méthodologique).
