# Modèle économique et social de la France (projet « Présidentielle »)

Modèle quantitatif destiné à servir de socle à un simulateur public de politiques publiques. Il n'utilise que des
données ouvertes. Version 0.8 du modèle (novembre 2026).

## Version 0.8 (phase 3.1, 23 novembre 2026)

Consolidation empirique et distribution dynamique des effets.

- Audit de la v0.7 (dont un défaut de code dans la fermeture) : `doc/18_audit_v07_phase31.md`.
- Modèle v0.8 (fermeture estimée : ρ et θ contraints par la durée des écarts de production AMECO/FMI ; incidence des
  prélèvements sur les entreprises ; corrections de la distribution) : `doc/19_modele_v08.md`.
- Registre des paramètres v0.8 (définition, valeur, intervalle, source, méthode, confiance, date) : `doc/20_registre_parametres_v08.md`.
- Nouveau module M16 (distribution dynamique des effets entre ménages) : `src/m16_distribution_dynamique.py`.
- Scripts (backtest 2010-2025, estimation de θ, sensibilité, décomposition v0.7/v0.8, diagnostic zone euro,
  réoptimisation), résultats et livrables : `phase31/` (rapport PDF `phase31/livrables/rapport_phase31_v08.pdf`,
  `distribution_effets_v08.xlsx`, `comparaison_v07_v08.xlsx`).
- Tests automatisés : `tests/test_phase31.py` (résultats dans `phase31/resultats/tests_phase31.xml` et en annexe du rapport).
- Les versions 0.6 (`rapport/`) et 0.7 (`phase3/`) restent disponibles ; leurs résultats ne sont pas modifiés.

## Version 0.7 (phase 3, 23 novembre 2026)

Comportements économiques, fiabilisation du modèle et première optimisation des politiques publiques.

- Audit de la v0.6 : `doc/15_audit_v06_phase3.md` (paradoxe des chocs d'offre : cause structurelle, absence de PIB potentiel).
- Registre des paramètres de comportement (valeurs basse, centrale, haute ; sources) : `doc/16_parametres_comportements_v07.md`.
- Équations ajoutées ou modifiées : `doc/17_modele_v07.md` (PIB potentiel, fermeture sur l'écart de production avec anticipation,
  emploi et approfondissement du capital, Phillips prix, épargne de précaution, rigidité salariale, transfert de bénéfices,
  trésorerie, TVA asymétrique, délocalisation énergétique, stabilisateur chômage, R&D et formation exploratoires).
- Nouveau module M15 (offre de travail, OpenFisca) : `src/m15_offre_travail.py` ; groupes de ménages dans `src/m10_couplage.py`.
- Scripts, résultats et livrables : `phase3/` (rapport PDF `phase3/livrables/rapport_phase3_v07.pdf`, comparaison
  v0.6/v0.7 et stratégies en Excel).
- Tests de cohérence comportementale : `tests/test_phase3.py` (12 tests, tous réussis le 23 novembre 2026).
- La v0.6 reste disponible (étiquette `v0.6`) ; ses résultats sont dans `rapport/resultats/`.

## Contenu

- `doc/` : documentation.
  - Décisions : `00_decisions.md`, A1-A15.
  - Plan et état d'avancement : `01_plan_des_lots.md`.
  - Registre des données : `02_registre_des_donnees.md`.
  - Modules :
    - M1 démographie ;
    - M3 cadre comptable ;
    - M4 population et législation ;
    - M5 bloc productif ;
    - M7-M8 comportements et modèle bouclé ;
    - M8 trajectoire de référence (`M8_reference.md`) ;
    - M9 activité et retraites ;
    - M10 couplage micro-macro ;
    - M11 zone euro ;
    - M13 comportements des hauts revenus.
  - Rapport de validation intégrale : `07_validation_integrale.md`.
  - Simulateur : `08_simulateur.md`.
  - Déploiement : `09_deploiement.md`.
  - Dossier de relecture externe : `10_dossier_relecture.md`.
- `src/` : modules M1-M13.
- `tests/` : un script de validation par module, plus la validation de l'approximation additive de l'interface.
- `simulateur/` :
  - catalogue de mesures (39 curseurs) ;
  - exécution d'un scénario ;
  - ménages types ;
  - restitution HTML ;
  - précalcul des variantes et marges d'incertitude ;
  - interface de test ;
  - serveur de calcul exact.
- `scenarios/` : scénarios d'exemple.
- `deploiement/` : conteneur Docker du service de calcul exact.
- `resultats/` : rapports de validation, exemples de restitution, variantes précalculées, interface de test,
  empreintes des données.

## Utilisation

**Installation.** `pip install -r requirements.txt` (Python 3.11 ou plus). Au premier lancement, les scripts
téléchargent les données dans `data/raw/` (non versé) et contrôlent leurs empreintes SHA-256. Le compte de
référence est ensuite recalé, en environ 10 minutes, puis mis en cache.

**Simuler un scénario.**

```
python3 -m simulateur.executer scenarios/exemple_A_relance.json
```

Le résultat est un fichier JSON, accompagné d'une page HTML de restitution, dans `outputs/`. Il contient la version
du modèle et les empreintes du code et des données.

**Interface de test.**

```
python3 -m simulateur.precalcul              # variantes élémentaires (environ 45 minutes)
python3 -m simulateur.incertitude_variantes  # marges d'incertitude (environ 1 heure)
python3 -m simulateur.interface              # outputs/interface_test.html
python3 -m simulateur.serveur                # http://localhost:8765, avec calcul exact
```

**Validation.** `python3 tests/validation_<module>.py` pour les modules M1, M3, lot5_cas_types, M4, prestations,
M5, M7, M8, M9, M10, M11 et M12. `python3 tests/validation_additivite.py` valide l'approximation additive de
l'interface.

Le premier lancement de M4 télécharge le recensement 2022 (650 Mo).

**Licence.** OpenFisca-France est sous licence AGPL-3.0.
