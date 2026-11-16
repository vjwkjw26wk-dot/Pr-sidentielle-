# Diagnostic d'accès réseau

## 16 novembre 2026, 15 h 50 — réseau ouvert

Tests réels depuis l'environnement de calcul (`curl`, `pip install`, téléchargements scriptés).

| Canal | Résultat |
|---|---|
| PyPI (`pip install`) | **Fonctionne** : openfisca-france 177.0.0, statsmodels, scipy, pandas, openpyxl installés |
| www.insee.fr (fichiers xlsx, zip, pdf) | **Fonctionne** |
| bdm.insee.fr (séries) | Répond |
| ec.europa.eu (API Eurostat) | **Fonctionne** |
| www.data.gouv.fr, www.statistiques.developpement-durable.gouv.fr | Répondent |
| data-api.ecb.europa.eu, api.db.nomics.world, raw.githubusercontent.com | Répondent |
| sdmx.oecd.org | Refusé (403) |
| api.insee.fr, webstat.banque-france.fr | Pas de réponse lors du test (à retester avant le lot 3b, qui a besoin des comptes financiers de la Banque de France) |

Les lots 3 et 5, bloqués le matin, ont été repris (voir `01_plan_des_lots.md`).

## 16 novembre 2026, 15 h 30 — état antérieur (pour mémoire)
PyPI injoignable, téléchargements HTTPS refusés par le proxy (403) pour tous les sites statistiques ; seul `git clone` depuis GitHub et la lecture de pages par l'outil web fonctionnaient.
