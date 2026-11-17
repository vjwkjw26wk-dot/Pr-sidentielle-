# M11 — Couplage France-zone euro (version 0.1)

**État : construit et testé.** Ce module ajoute autour du modèle bouclé M8 :
- la politique monétaire commune ;
- la transmission aux taux longs français ;
- une prime de risque sur la dette ;
- la demande des partenaires de la zone euro.

Ce n'est pas un modèle multi-pays : les partenaires sont résumés par quelques élasticités.
Code : `src/m11_europe.py`. Test : `tests/validation_M11.py`. Rapport : `resultats/validation_M11.md`.

## 1. Équations et paramètres

| Élément | Forme | Valeur | Statut |
|---|---|---|---|
| Règle de taux de la BCE (Euribor 3 mois, 1999-2019) | i = a + ρ i₋₁ + b π + c écart | ρ = 0,73 (t = 6,2) ; b = 0,39 (t = 2,2) ; c = 0,30 (t = 3,3) ; réponse de long terme à l'inflation 1,44 | **estimé** |
| Transmission au taux long français (1999-2024) | Δ taux long = α + β Δ i | β = 0,38 (t = 3,7) | **estimé** |
| Prime de risque | Δ taux long = θ × Δ dette (pt de PIB) | θ = 3 points de base par point de dette | hypothèse C (sensibilité 0 à 5) |
| Poids de la France dans la zone euro | — | 20 % du PIB | observé |
| Part de la zone dans les importations françaises | — | 55 % | ordre de grandeur des douanes |
| Multiplicateur des exportations des partenaires | — | κ = 1 | hypothèse C |
| Élasticité des importations de l'UE à l'activité des partenaires | — | 1,5 | cohérente avec l'équation d'importations française (1,4) |

**Écart de production.** Pour la France, il est mesuré par l'écart de chômage, avec la loi d'Okun (1,5 point de PIB
par point de chômage), et non par l'écart de PIB. Ce dernier inclut des effets d'offre durables (emplois publics,
population active), qui ne sont pas des tensions conjoncturelles.

**Résolution.** M8 est simulé, puis on en déduit les écarts de la zone, la réaction de la BCE et des marchés. M8 est
alors resimulé avec les nouveaux taux et la nouvelle demande mondiale. Quatre itérations suffisent.

## 2. Validation de la règle de taux

En simulation dynamique avec l'inflation et l'écart de production observés :
- **2000-2012** : la règle suit l'Euribor à 0,5-1 point près.
- **2015-2021** : elle ne reproduit pas les taux négatifs ni les achats d'actifs (plancher effectif des taux, politique non conventionnelle).
- **2022-2023** : la remontée est anticipée d'un an (3,1 % simulé en 2022 contre 0,35 %), puis le niveau de 2024 est retrouvé (3,7 % contre 3,6 %).

## 3. Variantes (écarts au compte central, base 2022, fermeture d'offre)

| Variante (effet en 2035) | PIB | Taux BCE | Taux long français | Solde public | Dette |
|---|---|---|---|---|---|
| Dépense publique française +1 pt de PIB, sans rétroaction | +0,22 % | — | — | −0,70 pt | +5,0 pt |
| Même mesure, avec BCE et partenaires | +0,22 % | ≈ 0 (+0,10 en 2026) | ≈ 0 | −0,73 pt | +5,3 pt |
| Même mesure, avec en plus la prime de risque | +0,19 % | ≈ 0 | +0,17 pt | −0,88 pt | +5,9 pt |
| Relance coordonnée dans toute la zone (+1 pt partout) | +0,16 % (+1,62 % en 2024) | +0,6 pt en 2025-2027 | +0,22 pt | −1,19 pt | +7,8 pt |
| Transferts aux ménages +1 pt de PIB, avec rétroactions | +0,03 % | ≈ 0 | +0,31 pt | −1,37 pt | +10,2 pt |

**Lecture.**
- **Mesure française isolée.** La BCE réagit peu, car la France ne pèse que 20 % de la zone. La rétroaction européenne est donc faible.
- **Relance coordonnée.** Elle soutient davantage l'activité au départ (+1,6 % contre +1,4 %), mais elle déclenche une hausse des taux de la BCE (+0,6 point pendant trois ans). Le coût en intérêts alourdit la dette française de près de 2 points de plus à l'horizon 2035.
- **Dette élevée.** La prime de risque ajoute un effet boule de neige modéré : +0,3 point de taux long et +1 point de dette pour un déficit permanent de 1 point de PIB.

## 4. Limites

- Pas de modèle des partenaires : multiplicateurs et élasticités calibrés.
- Les taux n'agissent que sur l'investissement (coût d'usage) et sur les intérêts de la dette. L'effet des taux sur la consommation et le logement n'est pas estimé, ce qui sous-estime l'efficacité de la politique monétaire.
- Pas de plancher des taux ni de politique monétaire non conventionnelle.
- Pas de taux de change : la zone euro est traitée comme fermée vis-à-vis du reste du monde, dont la demande reste exogène.
- Mécanismes européens (règles budgétaires, budget de l'UE, fonds de relance) non représentés.
