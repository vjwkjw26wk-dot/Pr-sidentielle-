# Chantier B — compte des sociétés intégré (phase 4.3)

Module `src/m21_societes.py` ; intégration dans `src/m8_modele.py` derrière l'interrupteur `SPEC["societes"] = "compte"`
(défaut `"v09"` : v0.9 reproduite à l'identique, test `test_v09_reproduite_apres_phase43`). Scripts : `b2_estimation.py`
(estimations et tests hors échantillon), `b3_backtest_societes.py` (rétrosimulations intégrées), `b4_compte_isole.py`
(compte seul, moteurs observés), `b5_autofinancement.py` (lien investissement-autofinancement).

Données : Eurostat `nasa_10_nf_tr` (comptes de secteurs, 1995-2025) et `nasa_10_f_bs` (bilans consolidés de S11 :
F3 + F4 au passif, F2 + F3 + F4 à l'actif, `data/raw/eurostat_nasa_10_f_bs_S11_CO_FR.json`, téléchargé pour ce chantier).
Aucune série complétée ni extrapolée.

## 1. Équations retenues

| Bloc | Équation | Statut |
|---|---|---|
| EBE de S11 | EBE_B × EBE marchand simulé / EBE marchand de base (S11 ⊂ branches marchandes) | identité + [C] |
| Intérêts versés | r_app × dette_{t−1} ; Δr_app = μ (1,29 (0,77 r3m + 0,23 r10) + 3,42 − r_app_{t−1}), μ = 0,60 | [E] 1999-2024, R² 0,81 |
| Intérêts reçus | rapport aux intérêts versés de l'année de base (0,70-0,82 depuis 2010) | [C] |
| IS de S11 | IS_B × résultat courant avant impôt / base × facteur fiscal | identité ; facteur : rapport des taux légaux × transfert de bénéfices (mesure) ou taux apparent observé (rétrosimulation) |
| IS de S12 | indexé sur le PIB nominal | [C] |
| Dividendes distribués aux détenteurs finals | ρ_B × résultat après intérêts et IS de l'exercice t − 1 | ρ_B [C], règle [H] |
| Répartition | ménages 42 %, reste du monde 50 %, APU 8 % (base 2019) ; part nette à la charge de S11 κ = 0,50 | [C] |
| D43, D44-45, autres opérations courantes, autres emplois en capital | ratio à la VA de S11 de l'année de base | [C] |
| Épargne brute, capacité de financement | B8G = EBE − intérêts − dividendes − D43 + D44-45 − IS + autres ; B9 = B8G − FBCF − autres | identités |
| FBCF de S11 | FBCF de base × FBCF des branches marchandes en valeur simulée / base | [C] |
| Dette de S11 | dette_B × PIB nominal + φ Σ (−(B9 − B9_B × PIBn)), φ = 1,06 (± 0,31) | φ [E] 1997-2019 |
| Revenus de la propriété des ménages | D4 de base × PIB nominal + part des ménages × (dividendes − dividendes de base × PIB nominal) | identité |
| Reste du monde | dividendes versés aux non-résidents : part de base × écart des dividendes ; entre dans le RNB et le solde extérieur | identité |
| Profits induits par les mesures (M14) | entrent dans le résultat de S11 ; plus de second canal de distribution (double compte supprimé) | identité |

## 2. Choix et variantes écartées

- **Dividendes.** L'équation de Lintner n'est pas identifiée : vitesse de rappel −0,09 (± 0,06) ; le taux de distribution
  a doublé entre 1997 et 2019 (0,16 → 0,36), sans cible stable. Hors échantillon, elle prédit moins bien que la règle
  proportionnelle (origine 2014 : 28,7 % contre 16,6 %). Retenu : distribution proportionnelle au résultat de l'exercice
  précédent, au taux de l'année de base. La tendance passée n'est pas extrapolée ; c'est la principale source d'erreur en
  2021-2024 (dividendes sous-estimés de 9 à 36 %). Variante de lissage (vitesse 0,3) disponible.
- **Fiscalité des dividendes.** Effets non identifiés de façon robuste : le signe dépend de la spécification (PFU +0,08 en
  croissance dans l'équation de Lintner, −0,44 en niveau avec tendance). Nuls en central ; variante `fiscalite_dividendes`.
- **Solde des dividendes de S11** (versés − reçus) : écarté comme variable de comportement, car c'est la différence de deux
  flux bruts d'environ 200-300 Md€ (variabilité du taux de distribution deux fois plus forte que le flux distribué aux
  détenteurs finals, 0,25 contre 0,12).
- **Taux apparent.** Le taux court domine : une spécification sur le seul taux à 10 ans est rejetée (R² 0,51). Estimée
  jusqu'en 2019, la vitesse de renouvellement est presque totale (0,83) et surestime le taux de 2,1 points en 2023-2024 ;
  2022-2024 étant le seul épisode de hausse, l'estimation est étendue à 2024 (0,60). Variantes : 0,35 et 0,83.
- **Intérêts reçus.** L'équation de taux sur les actifs liquides est rejetée : R² 0,48, transmission 2,8, car les intérêts
  reçus incluent ceux des prêts aux filiales non résidentes, absents des actifs consolidés. Indexer les actifs sur le PIB
  sous-estimait les intérêts reçus de 11 à 40 Md€. La règle retenue lie les intérêts reçus aux intérêts versés.
- **IS.** Le taux apparent de l'IS ne suit pas le taux légal : élasticité −0,10 (± 0,29) sur 1997-2019, car les baisses de
  taux (33 → 25 %) ont été compensées par des élargissements d'assiette. La proportionnalité au taux légal (v0.9) est
  conservée pour évaluer une mesure à assiette donnée. Dans les rétrosimulations, le taux apparent observé est injecté,
  comme les autres politiques.
- **Investissement et autofinancement.** Ni le taux d'épargne, ni le taux de profit, ni sa variation, retardés, ne sont
  significatifs dans une équation d'accélérateur de S11 (p = 0,26 à 0,59). Aucun canal financier n'est ajouté :
  l'investissement reste déterminé par la demande et le coût d'usage.

## 3. Résultats

**Compte isolé** (moteurs observés, `b4_compte_isole.py`). Sur les origines 2010, 2014 et 2019, à 5-10 ans :
- intérêts nets : écart de −6 à +12 Md€ ;
- IS : écart de −3 à +2 % ;
- épargne : écart de −10 à +9 % ;
- dette des SNF : écart de −19 à +2 % (2020 : prêts garantis par l'État, absents du modèle) ;
- dividendes : écart de −37 à +32 %, dû à la tendance du taux de distribution.

**Intégré** (`b3_backtests.log`). Le compte hérite des erreurs d'EBE du modèle (−16 à −19 % en 2023-2024, profits
exceptionnels de 2022-2023 non expliqués, déjà signalés au chantier A). Les agrégats macroéconomiques sont presque
inchangés (PIB, prix, emploi : au plus 0,1 point d'écart avec T1 ; dette publique : −0,3 à −3,3 points selon l'origine,
car le taux apparent observé de l'IS est désormais injecté).

**Identités.** Épargne et capacité de financement exactes, à moins de 1e-9 M€, à chaque année de toutes les simulations.
Les revenus de la propriété des ménages sont reconstruits exactement à partir des dividendes (test
`test_p4_identites_et_lien_menages`).

## 4. Limites

- La tendance du taux de distribution n'est pas modélisée : une projection longue la fige au niveau de l'année de base.
- Les intérêts et le D44 des ménages restent indexés sur le PIB : la hausse des taux ne relève pas leurs revenus de
  placement, hors dividendes.
- S12 n'a pas de comportement propre.
- Le lien capacité de financement → dette repose sur une estimation fragile (φ = 1,06 ± 0,31 ; variantes 0,5 et 1,5).
- Les profits induits par les mesures sont distribués au taux moyen (0,36 du résultat), et non plus au taux marginal M14
  (0,5).
