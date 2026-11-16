# Module M3 — Cadre comptable T0 (couche 1 de A1)

**Statut : construit pour les comptes non financiers, le patrimoine financier net par secteur et la dette publique (16 novembre 2026). À compléter : bilans financiers par instrument et matrice « de qui à qui » des revenus de la propriété (lot 3b).**

## Contenu
Matrice des transactions non financières de la France, par secteur institutionnel et par année, 2019-2025, en M€ courants (base 2020), et comptes de patrimoine financier.

- **Secteurs** : S11 sociétés non financières, S12 sociétés financières, S13 administrations publiques, S14 ménages, S15 ISBLSM, S1N pseudo-secteur portant les impôts nets des subventions sur les produits, S2 reste du monde.
- **Lignes** : 33 opérations « feuilles » sans recouvrement : une ligne biens et services (P1, impôts nets sur produits, P7 en ressources ; P2, P3, P51G, P52, P53, P6 en emplois), D11, D12, D21, D29, D31, D39, D41, D421, D422, D43, D441-D443, D45, D51, D59, D611-D614, D61SC, D62, D71, D72, D74, D75, D76, D8, D91, D92, D99, NP.
- **Convention** : pour chaque secteur, emplois (E) et ressources (R) ; le reste du monde est vu de son propre point de vue.

## Identités
```
(1) Pour chaque opération o : Σ_secteurs E[o,s] = Σ_secteurs R[o,s]
(2) Pour chaque secteur s : B9[s] = Σ_o R[o,s] − Σ_o E[o,s]
(3) Σ_s B9[s] = 0     (conséquence de (1) et (2), contrôlée séparément)
(4) PIB = Σ VA + impôts nets sur produits = P3 + P5 + P6 − P7
(5) PFN[s,t] = PFN[s,t−1] + B9F[s,t] + AF[s,t]       (AF : réévaluations et changements de volume)
(6) Dette[t] = Dette[t−1] − B9[S13,t] + ASF[t]       (ASF : ajustement stock-flux)
```
Les écarts des données publiées sont reportés dans un compte « ECART » (lignes) et une ligne « ECART_SECTEUR » (colonnes), sans modifier aucune opération. L'écart B9 − B9F (comptes non financiers et financiers), AF et ASF sont des grandeurs explicites du cadre, exogènes en simulation tant qu'elles ne sont pas modélisées.

## Validation (`tests/validation_M3.py`, rapport `outputs/validation_M3.md`)
- **Données publiées** : de 5 à 10 lignes sur 33 présentent un écart, au plus 4 M€ ; B9 recalculé à au plus 4 M€ du B9 publié. Ce sont des arrondis.
- **Cadre réconcilié** : identités (1) à (3) exactes (écart nul en virgule flottante) pour chaque année 2019-2025.
- **PIB** : reconstitué à 1 M€ près (production) et 2 M€ près (demande) des valeurs publiées.
- **Finances publiques**, conformes à la publication de l'Insee de mai 2026 : solde −5,4 % (2023), −5,8 % (2024), −5,1 % du PIB (2025) ; dette 109,5 %, 112,6 %, 115,7 % ; dépenses 57,3 % du PIB en 2025.
- **Stocks** : Σ des patrimoines financiers nets, reste du monde compris = 0 à 1 M€ près.

## Limites et suite (lot 3b)
1. Les revenus de la propriété (D41, D42) sont connus par secteur payeur et par secteur receveur, pas par paire de secteurs. Le cadre stock-flux complet requiert une matrice « de qui à qui », à estimer à partir des comptes financiers de la Banque de France (qui-à-qui par instrument), en données ouvertes.
2. Bilans financiers par instrument (dépôts, titres de dette, crédits, actions, assurance-vie) : nécessaires pour faire dépendre les intérêts des taux. Source prévue : Eurostat `nasa_10_f_bs` par instrument.
3. Patrimoine non financier (logements, terrains) : non intégré.
4. Les données 2025 sont semi-définitives (révision attendue en mai 2027).
