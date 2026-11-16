# Modèle économique et social de la France (projet « Présidentielle »)

Modèle quantitatif destiné à servir de socle à un simulateur public de politiques publiques. Données ouvertes uniquement.

- `doc/` : décisions (`00_decisions.md`), plan des lots et état d'avancement (`01_plan_des_lots.md`), registre des données (`02_registre_des_donnees.md`), documentation des modules (M1 démographie, M3 cadre comptable, M4 population).
- `src/` : code des modules. `tests/` : scripts de validation. `resultats/` : rapports de validation et empreintes des données téléchargées.

Installation : `pip install -r requirements.txt` (Python 3.11 ou plus). Les données sont téléchargées par les scripts dans `data/raw/` (non versé) au premier lancement ; leurs empreintes SHA-256 sont contrôlées.

Validation : `python3 tests/validation_M1.py`, `python3 tests/validation_M3.py`, `python3 tests/validation_lot5_cas_types.py`, `python3 tests/validation_M4.py` (ce dernier télécharge le recensement 2022, 650 Mo).

Note de licence : OpenFisca-France est sous licence AGPL-3.0.
