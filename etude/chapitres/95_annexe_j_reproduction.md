# Guide technique de reproduction des simulations {#sec:annexe-j}

## J.1 Environnement logiciel

- Dépôt : `vjwkjw26wk-dot/Pr-sidentielle-`, branche `phase43` (la branche `main` conserve la version 0.8, immuable).
  L'étiquette de gel de cette étude est indiquée dans `GEL.md` à la racine du dépôt.
- Python 3.13 ; bibliothèques : numpy, pandas, scipy, statsmodels, matplotlib, OpenFisca-France 177.0.0.
- Compilation de l'étude : pandoc (≥ 3), XeLaTeX (TeX Live), polices TeX Gyre.
- Données : `data/raw/` (téléchargées par `src/telechargement.py`, empreintes SHA-256 dans `data/raw/_registre.json`).

## J.2 Configuration de référence (gel technique) {#sec:gel}

| Élément | Valeur | Code |
|---|---|---|
| Configuration du modèle | P4 : v0.9 + prix de VA « frontière » + sans effet de tension + compte des sociétés | `M8.configurer_phase4()` |
| Environnement | `Environnement.charger("p4", "part_constante")`, base 2022, horizon 2047 | `src/m23_regimes.py` |
| Environnement de traduction | `Environnement.charger("p4", "historique")` | idem |
| Régime principal | `regime("R2")` : règle R2 figée, taux exogènes, jeu central | idem |
| Variante européenne de référence | « conforme » | `src/m26_europe_institutions.py` |
| Corpus | `src/m27_corpus.py`, daté du 24 novembre 2026 | — |

Le premier chargement d'un environnement le calibre (environ 50 minutes de calcul par environnement) et le met en cache
dans `outputs/` ; les chargements suivants vérifient l'empreinte des paramètres et la trajectoire de contrôle.

## J.3 Commandes

```
# environnements (une fois)
python3 phase5/construire_environnement.py p4 part_constante
python3 phase5/construire_environnement.py p4 historique
python3 phase5/construire_environnement.py p4_sigma03 part_constante
python3 phase5/construire_environnement.py p4_sigma06 part_constante
python3 phase5/construire_environnement.py p4_prix_v09 part_constante

# campagne de simulations des programmes (≈ 15 à 20 minutes par candidat)
python3 phase7/campagne.py melenchon
python3 phase7/campagne.py le_pen
python3 phase7/campagne.py philippe
python3 phase7/multiplicateurs.py

# stratégies de test S1-S5 et robustesse (phase 5)
python3 phase5/lot53_strategies.py
python3 phase5/lot53_structurels.py
python3 phase5/lot53_structurels_monetaires.py
python3 phase5/lot53_environnements.py

# tests
python3 -m pytest -q tests/test_finalisation.py tests/test_phase6.py tests/test_lot53.py \
    tests/test_lot52.py tests/test_phase5.py tests/test_phase43.py

# étude : tableaux, figures, chapitres de résultats, puis PDF
python3 etude/generer.py
bash etude/compiler.sh
```

## J.4 Simuler un programme ou une mesure

```python
import m23_regimes as G, m25_programmes as P, m27_corpus as C
env_h = G.Environnement.charger("p4", "historique")
env = G.Environnement.charger("p4", "part_constante")
mesures, hors_modele = C.mesures("philippe", env.reference, "conforme")   # lecture A
prog = P.programme(P.traduire([m[:3] for m in mesures], env_h, "philippe", microsimulation="calcul"))
effet = G.evaluer(env, G.regime("R2"), prog)["ecart"]                     # écarts à la référence
# lecture B : objectif de solde
obj = G.ObjectifBudgetaire(cibles={2027: -6.0, 2032: -2.5}, parts={"prestations": 2/3, "conso_publique": 1/3})
effet_B = G.evaluer(env, G.regime("R2"), prog, objectif=obj)["ecart"]
```

Une mesure isolée se simule en ne gardant que ses éléments dans `mesures` ; une mise en œuvre partielle ou retardée
avec la fonction `modifier` de `phase7/campagne.py` ; un régime alternatif avec `G.regime(code, monetaire=…,
structurels=…, **options)` (voir `G.REGIMES_ROBUSTESSE`).

## J.5 Mettre à jour le corpus après les publications des candidats

1. Ajouter ou modifier les mesures dans `src/m27_corpus.py` (source dans `SOURCES`, montant, calendrier, canal, règle,
   qualification européenne) et, le cas échéant, l'objectif dans `OBJECTIFS`.
2. Lancer `python3 -m pytest -q tests/test_phase6.py tests/test_finalisation.py` (intégrité du corpus, recoupements).
3. Relancer la campagne du candidat (`phase7/campagne.py <candidat>`), puis `etude/generer.py` et `etude/compiler.sh`.

La liste des éléments à actualiser figure au chapitre \ref{sec:conclusion} (section « Questions ouvertes »).
