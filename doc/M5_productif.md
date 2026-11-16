# M5 — Bloc productif sectoriel (version 0.1 : socle entrées-sorties)

État : **socle statique validé, comportements non encore estimés.** Ce document décrit ce qui existe, ce qui a été testé et ce qui manque. Le bloc n'est pas encore un modèle dynamique : les équations de comportement font l'objet de l'étape suivante (lot 7).

## 1. Rôle dans le modèle

Le bloc productif relie la demande (consommation, investissement, dépenses publiques, exportations) à la production, aux importations, à l'emploi et aux prix, par produit. C'est lui qui doit répondre aux questions de la phase 2 : transmission d'un choc de prix de l'énergie, dépendance aux importations, effets d'une réindustrialisation, d'une hausse des salaires ou de l'impôt sur les sociétés.

## 2. Données

| Donnée | Source | Couverture | Usage |
|---|---|---|---|
| Tableau entrées-sorties symétrique produit × produit, prix de base, séparé en flux intérieurs et importés | Eurostat `naio_10_cp1700` (TOTAL, DOM, IMP) | France, 2010-2022 (2023-2024 annoncées mais vides) | Coefficients techniques, valeur ajoutée, emplois finals |
| Même tableau aux prix de l'année précédente | Eurostat `naio_10_pyp1700` (TOTAL seulement ; DOM et IMP vides) | 2011-2022 | Prix de production par produit |
| Tableau des ressources aux prix courants et de l'année précédente | Eurostat `naio_10_cp15`, `naio_10_pyp15` | 2010-2022 | Prix d'importation par produit |

**Anomalie de source repérée et contournée.** Dans `naio_10_pyp1700`, la ligne des importations (P7) est désalignée pour la France de 2014 à 2019 (valeurs dupliquées d'un produit à l'autre, prix d'importation implicites de −100 % à +120 %). Les prix d'importation sont donc tirés des tableaux des ressources, cohérents au million d'euros près avec les tableaux symétriques aux prix courants.

## 3. Nomenclature (décision A9)

64 produits de la nomenclature A64 (niveau le plus fin publié de façon homogène), dont trois produits énergétiques distincts : industries extractives (B : pétrole brut, gaz, minerais), cokéfaction et raffinage (C19), électricité-gaz-vapeur (D). Ce niveau permet de représenter les filières industrielles de la réindustrialisation (métallurgie, chimie, pharmacie, automobile, aéronautique, électronique, machines). Pas d'entreprises individuelles.

## 4. Équations

Notations : Ad et Am, coefficients des consommations intermédiaires intérieures et importées par unité produite ; av, valeur ajoutée et impôts nets sur les produits par unité produite ; fd, demande finale adressée à la production intérieure.

- Quantités (Leontief) : x = (I − Ad)⁻¹ fd ; importations m = Am x + fm.
- Prix (coûts) : p = (pm · Am + pv · av)(I − Ad)⁻¹ ; pm, prix des importations par produit ; pv, prix de la valeur ajoutée unitaire (salaires unitaires, marges, impôts sur la production).
- Contenu en importations : 1ᵀ Am (I − Ad)⁻¹.

Hypothèses de cette version : coefficients techniques fixes à l'année de base ; pas de substitution entre intrants ni entre produit intérieur et importé ; valeur ajoutée unitaire exogène.

## 5. Validation (détail : `resultats/validation_M5.md`)

1. **Identités comptables** : vérifiées pour chaque année 2010-2022 (écarts ≤ 2 M€, arrondis de publication).
2. **Test rétrospectif des prix, 2012-2022**, coefficients de N−1 et chocs observés en N :
   - transmission des seuls prix d'importation : erreur absolue moyenne de 0,9 à 1,7 point par produit en année ordinaire, 6,2 points en 2022 ; elle explique environ la moitié de la hausse de 2022 (+4,9 % prévu contre +9,7 % observé) ;
   - avec les prix observés de la valeur ajoutée : erreur de 0,3 à 0,8 point et corrélation de 0,89 à 0,98 en 2012-2019 ; la cohérence du modèle de prix est bonne en régime normal ;
   - **en 2020 et 2022 le modèle se dégrade** (erreur 2,0 et 3,0 points ; en 2022, raffinage +74 % prévu contre +43 % observé, métallurgie +62 % contre +31 %). En 2022, les prix à la consommation des ménages sont surestimés (+9,0 % contre +5,6 %). Causes : substitutions entre intrants et compression ou gonflement des marges (non représentés à coefficients fixes), bouclier tarifaire sur l'énergie, et définition du prix de la valeur ajoutée qui absorbe les changements de coefficients.
3. **Test rétrospectif des quantités** : production en volume prévue par la demande finale observée, erreur absolue moyenne de 0,9 à 1,6 % par produit et croissance d'ensemble à ±0,9 point près, sauf 2020 (erreur 5,4 % par produit).
4. **Illustrations (2021)** : contenu en importations de la demande finale intérieure 0,18 € par € ; produits les plus dépendants : raffinage (0,73), aéronautique et autres matériels de transport (0,52), métallurgie (0,50), automobile (0,48). Une hausse de 50 % des prix de l'énergie importée, à marges fixes, élève les prix de production de 1,3 % et les prix à la consommation de 1,7 %.

## 6. Ce que l'on peut et ne peut pas dire à ce stade

- Robuste : la structure des dépendances (contenu en importations, multiplicateurs de production, propagation des coûts) et les ordres de grandeur de court terme hors grands chocs.
- Dépendant d'hypothèses : tout résultat de moyen terme et tout grand choc, tant que la substitution, les marges, l'emploi, l'investissement et les capacités ne sont pas estimés.
- Non couvert : flux énergétiques et matériels physiques (tonnes, TWh), emploi par branche, capital, finances des entreprises. Ils sont prévus aux étapes suivantes.

## 7. Étapes suivantes (lot 7)

1. Séries par branche 1995-2025 (comptes nationaux A64 : production, valeur ajoutée, emploi, salaires, investissement, capital ; Eurostat `nama_10_a64`, `nama_10_a64_e`, `nama_10_a64_p5`, `nama_10_nfa_st`) et comptes physiques de l'énergie (`env_ac_pefasu`).
2. Équations de comportement estimées par branche (modèles à correction d'erreur en panel) : prix et taux de marge, demande de travail, investissement et capacités, partage intérieur-importé (élasticités prix et demande), exportations, avec tests de stabilité.
3. Bouclage dynamique annuel avec les comptes sectoriels (M3), les ménages (M4) et les finances publiques ; simulations rétrospectives sur plusieurs années (2015-2023), en particulier 2022.
