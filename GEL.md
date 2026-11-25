# Gel technique du modèle — version 1.0 (25 novembre 2026)

Étiquette git : `v1.0-gel-2026-11-25` (branche `phase43`). La branche `main` conserve la version 0.8, immuable ;
les versions 0.9, T1 et P4 restent sélectionnables (`m23_regimes.CONFIGURATIONS`).

## 1. Configuration de référence

| Élément | Valeur par défaut | Où |
|---|---|---|
| Modèle | **P4** = v0.9 + prix de VA « frontière » + sans effet de tension + compte des sociétés (M21) | `M8.configurer_phase4()` |
| Environnement | `Environnement.charger("p4", "part_constante")` : base 2022, horizon 2047, consommation publique et prestations hors pensions à part constante du PIB potentiel conventionnel | `src/m23_regimes.py`, `src/m8_reference.py` |
| Environnement de traduction des programmes | `Environnement.charger("p4", "historique")` | idem |
| Régime budgétaire | R2 figé : α 0,5 ; β 0,02 ; dette cible 90 % ; plafond 0,5 pt ; clause −1,5 ; parts 30/20/30/20 | `G.regime("R2")` |
| Régime monétaire | taux exogènes (Euribor observé à partir de 2027) | `RegimeMonetaire(type="exogene")` |
| Jeu de paramètres | central | `G.JEUX_PARAMETRES["central"]` |
| Variante européenne | conforme | `m26_europe_institutions.SCENARIOS` |
| Corpus | arrêté au 24 novembre 2026 | `src/m27_corpus.py` (`DATE_CORPUS`) |
| Lecture B | objectifs de solde annoncés, compositions [H] | `m27_corpus.OBJECTIFS`, `G.ObjectifBudgetaire` |

## 2. Configurations alternatives conservées

- Environnements : `p4_sigma03`, `p4_sigma06`, `p4_prix_v09` (calibrés, en cache), `v09`, `v08`.
- Régimes : `G.REGIMES_ROBUSTESSE` (10 régimes : R0, R1, R2 actif, R2 actif symétrique, BCE + prime, ancrage
  faible/fort, fermetures lente/rapide/chômage).
- Paramètres structurels modifiables sans recalibration : `G.STRUCTURELS` (17, valeurs basse/centrale/haute).
- Variantes européennes : conforme, contentieux, tension.
- Hypothèse de taux longs : OAT au dernier point observé (4,89 %) ou à la moyenne sur douze mois (3,82 %,
  `G.variante_oat()`).

## 3. Versions du code et des données

- Code : commit étiqueté `v1.0-gel-2026-11-25`.
- Données : `data/raw/` ; empreintes SHA-256 dans `data/raw/_registre.json` ; téléchargement par
  `src/telechargement.py` (sources ouvertes uniquement).
- Environnements calibrés : `outputs/` (non versionné, reconstructible) ; leur validité est vérifiée à chaque
  chargement par l'empreinte de tous les paramètres calibrés et une trajectoire de contrôle (~70 séries).
- Résultats de l'étude : `phase7/resultats/` (campagnes), `phase5/resultats/` (robustesse S1-S5).

## 4. Reproduction

```
# environnements (une fois ; ≈ 50 min de calcul chacun)
python3 phase5/construire_environnement.py p4 part_constante
python3 phase5/construire_environnement.py p4 historique
python3 phase5/construire_environnement.py p4_sigma03 part_constante
python3 phase5/construire_environnement.py p4_sigma06 part_constante
python3 phase5/construire_environnement.py p4_prix_v09 part_constante
# campagnes (≈ 20 à 30 min par candidat)
python3 phase7/campagne.py melenchon
python3 phase7/campagne.py le_pen
python3 phase7/campagne.py philippe
python3 phase7/multiplicateurs.py
# robustesse S1-S5
python3 phase5/lot53_strategies.py && python3 phase5/lot53_structurels.py
python3 phase5/lot53_structurels_monetaires.py && python3 phase5/lot53_environnements.py
# tests
python3 -m pytest -q tests/test_finalisation.py tests/test_phase6.py tests/test_lot53.py \
    tests/test_lot52.py tests/test_phase5.py tests/test_phase43.py
# étude
python3 etude/generer.py && bash etude/compiler.sh     # → etude/build/etude.pdf
```

## 5. Capacités et limites résiduelles

Voir `doc/28_gel_technique.md`.
