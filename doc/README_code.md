# Code du modèle — mode d'emploi

Arborescence attendue après copie depuis le projet (`modele/code/` → dossier local `modele/`) :

```
modele/
  src/telechargement.py       téléchargement scripté, cache, registre SHA-256 ; lecteur JSON-stat d'Eurostat
  src/insee_projections.py    lecture des 29 scénarios des projections de population 2026 de l'Insee
  src/m1_demographie.py       M1 v2 : moteur de projection par cohortes, générateur de scénarios, population active
  src/run_m1.py               projection de référence (sortie outputs/M1_reference.csv)
  src/m3_cadre_comptable.py   M3 : matrice des transactions par secteur, réconciliation, flux-stocks, dette
  tests/validation_M1.py      réplication des scénarios Insee (tests A et B)
  tests/validation_M3.py      identités et agrégats du cadre comptable
  tests/validation_lot5_cas_types.py   OpenFisca-France face à des cas types recalculés
  data/raw/                   créé au premier lancement (données téléchargées, non versées)
  outputs/                    rapports de validation
```

Installation : `pip install openfisca-france statsmodels pandas scipy openpyxl` (Python 3.11 ou plus ; testé en 3.13).
Durées indicatives : validation M1 environ 2 min (29 scénarios, ~75 Mo téléchargés au premier lancement) ; M3 quelques secondes ; lot 5 environ 30 s.
