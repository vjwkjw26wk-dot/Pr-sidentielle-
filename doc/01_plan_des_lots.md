# Plan des lots et état d'avancement

Statuts : **construit** (code, données, validation chiffrée livrés) · **en partie construit** · **à faire** · **bloqué**.
Mise à jour : 16 novembre 2026, soir (lot 4 version 1).

| Lot | Contenu | Critère de validation | Statut |
|---|---|---|---|
| 0 | Cadre : décisions, registre des données, dépôt, téléchargement scripté avec empreintes | — | construit |
| 1 | M1 Démographie v2 : cohortes 0-120 ans, méthode Insee 2026, générateur de scénarios ; population active à taux constants | Réplication des scénarios Insee ; identité démographique exacte | **construit** — 29 scénarios reproduits (population totale ≤ 3,4·10⁻⁵) ; générateur exact dans les directions Insee (voir `M1_demographie.md`) |
| 2 | Taux d'activité par âge sensibles aux règles de retraite ; composition des ménages | Projections de population active de l'Insee ; nombre de ménages observé | à faire |
| 3 | Cadre comptable T0 : comptes des secteurs, administrations publiques, dette | Identités exactes ; agrégats 2023-2025 reproduits | **en partie construit** — comptes non financiers 2019-2025, patrimoine financier net, dette : identités exactes, agrégats conformes à l'Insee (voir `M3_cadre_comptable.md`). Reste (3b) : bilans par instrument, matrice de qui à qui |
| 4 | Population de ménages et de foyers fiscaux | Marges publiées reproduites ; biais sur distributions jointes mesurés | **en partie construit** — vrais ménages du recensement 2022 (fichier détail ouvert), revenus ancrés sur la distribution fiscale DGFiP 2024 ; population et ménages conformes à l'Insee ; 38,3 M de foyers contre 41,6 M ; impôt encadré (82 à 113 Md€ avant réductions et crédits, contre au moins 101 Md€) mais non reproduit (voir `M4_population.md`) |
| 5 | Législation socio-fiscale (OpenFisca-France 177, licence AGPL-3.0) | Cas types ; masses d'impôts et de prestations face aux comptes publics | **en partie construit** — installé ; 11 cas types sur 11 conformes à l'euro près (IR, salaire net, RSA, allocations familiales). Masses d'IR : premier test sur la population M4 (part de foyers imposés par tranche conforme ; niveau encore encadré seulement). Reste : réductions et crédits d'impôt, prestations |
| 6 | Bloc productif entrées-sorties, énergie, commerce extérieur par produit | Équilibres ressources-emplois par produit ; contenu en importations | à faire (données accessibles : Insee TES, Eurostat `naio_10`) |
| 7 | Équations de comportement estimées | Tests de spécification ; rétrosimulation 2000-2019 | à faire (séries longues désormais téléchargeables ; statsmodels installé) |
| 8 | Couplage, convergence, retraites, finances publiques dynamiques | Convergence ; identités ; indépendance au point de départ | à faire |
| 9 | Validation intégrale | Écarts quantifiés et expliqués | à faire |

## Environnement de calcul
Depuis le 16 novembre 2026 après-midi, le réseau est ouvert : PyPI, Insee, Eurostat, data.gouv.fr, BCE et DBnomics répondent (OCDE `sdmx.oecd.org` refusé ; `api.insee.fr` et `webstat.banque-france.fr` sans réponse lors du test).

**L'espace de travail n'est pas conservé d'une session à l'autre** (le code du lot 1 v1 a été perdu ainsi). Le code est donc versé dans le projet sous `modele/code/`, et les données brutes ne sont jamais conservées : elles sont retéléchargées par script, et leurs empreintes SHA-256 sont consignées dans `modele/resultats/registre_telechargements.json`. Une révision des données publiées est ainsi détectée.

Pour reconstruire : copier `modele/code/` dans un dossier `modele/`, installer `openfisca-france statsmodels pandas scipy openpyxl`, puis exécuter `python3 tests/validation_M1.py`, `python3 tests/validation_M3.py`, `python3 tests/validation_lot5_cas_types.py` et `python3 tests/validation_M4.py` (premier lancement : téléchargement du recensement, 650 Mo, environ 17 min).

**Dépôt Git** : un compte GitHub est relié, mais aucun dépôt n'est accessible ; dès qu'un dépôt vide est créé et ouvert à l'application GitHub de Claude, le code y sera versé (décision A8).
