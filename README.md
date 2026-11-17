# Modèle économique et social de la France (projet « Présidentielle »)

Modèle quantitatif destiné à servir de socle à un simulateur public de politiques publiques. Données ouvertes uniquement.

## Contenu

- `doc/` :
  - décisions (`00_decisions.md`, A1-A15) ;
  - plan et état d'avancement (`01_plan_des_lots.md`) ;
  - registre des données (`02_registre_des_donnees.md`) ;
  - documentation des modules : M1 démographie, M3 cadre comptable, M4 population et législation, M5 bloc productif, M7-M8 comportements et modèle bouclé, M9 activité et retraites, M10 couplage micro-macro, M11 zone euro ;
  - rapport de validation intégrale (`07_validation_integrale.md`) ;
  - simulateur (`08_simulateur.md`).
- `src/` : modules M1-M12.
- `tests/` : scripts de validation, un par module.
- `simulateur/` : catalogue de mesures, exécution d'un scénario, ménages types, restitution HTML.
- `scenarios/` : scénarios d'exemple.
- `resultats/` : rapports de validation, exemples de restitution, empreintes des données téléchargées.

## Utilisation

Installation : `pip install -r requirements.txt` (Python 3.11 ou plus). Au premier lancement, les scripts téléchargent les données dans `data/raw/` (non versé) et contrôlent leurs empreintes SHA-256.

Simuler un scénario :

```
python3 -m simulateur.executer scenarios/exemple_A_relance.json
```

Le résultat est un fichier JSON accompagné d'une page HTML de restitution dans `outputs/`.

Validation : `python3 tests/validation_<module>.py`. Modules disponibles :
- M1, M3, lot5_cas_types, M4, prestations ;
- M5, M7, M8, M9, M10, M11, M12.

Le premier lancement de M4 télécharge le recensement 2022 (650 Mo).

Note de licence : OpenFisca-France est sous licence AGPL-3.0.
