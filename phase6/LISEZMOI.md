# Phase 6 et préparation des programmes

| Fichier | Rôle |
|---|---|
| `../src/m26_europe_institutions.py` | règles de droit de l'Union, qualification des mesures (niveaux 0-4), variantes conforme / contentieux / tension, amendes PDE, prime souveraine (doc 24) |
| `../src/m27_corpus.py` | corpus des programmes Mélenchon, Le Pen, Philippe (sources, montants, calendriers, canaux, règles de conversion) ; `mesures(candidat, reference, scenario)` (doc 25) |
| `../src/m25_programmes.py` | traduction des programmes : microsimulation calculée (`microsimulation="calcul"`), listes de mesures datées, mesures hors curseurs (`investissement_hors_apu`) |
| `simulabilite.py` | test de simulabilité des trois paquets (diagnostics seulement, aucun résultat comparatif) → `resultats/simulabilite.json`, `resultats/traductions_candidats.pkl` |
| `generer_doc_corpus.py`, `gabarit_doc25.md` | régénération de `doc/25_corpus_programmes.md` depuis le corpus |
| `../tests/test_phase6.py` | intégrité du corpus, recoupement des totaux LFI, conversions, variantes européennes, amendes |

Ordre d'exécution : `python3 phase6/simulabilite.py` (≈ 6-10 min, environnements P4 en cache) puis
`python3 phase6/generer_doc_corpus.py` après toute modification du corpus.
