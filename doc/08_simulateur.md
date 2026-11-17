# Phase 8 — Préparation du simulateur (prototype 0.1)

**État : prototype fonctionnel, en ligne de commande.** Un scénario décrit en JSON est exécuté par l'ensemble des
modèles (M1, M4, M8-M12). Le résultat est restitué dans un fichier JSON et dans une page HTML autonome, avec la fiche
de transparence exigée par le cahier des charges (§ 17.1).

Il n'y a pas encore de service en ligne : ni serveur, ni comptes, ni file d'attente de calculs.
Code : dossier `simulateur/`. Exemples : dossier `scenarios/`.

## 1. Utilisation

```
python3 -m simulateur.executer scenarios/exemple_A_relance.json
→ outputs/exemple_A_relance_resultats.json et .html
```

Format du scénario :

```json
{"nom": "...", "description": "...", "base": 2022, "horizon": 2030,
 "hypotheses": {"fermeture_offre": 0.15, "europe": true, "incertitude": 0, "profils": true},
 "mesures": [{"type": "depense_publique", "parametres": {"points_pib": 1.0, "debut": 2024}}, ...]}
```

`incertitude` donne le nombre de tirages Monte-Carlo (0 = aucun ; 20 à 40 recommandés ; environ 15 s par tirage).

## 2. Catalogue des mesures (`simulateur/catalogue.py`)

| Type | Mesure | Modèles mobilisés | Niveau de preuve |
|---|---|---|---|
| `depense_publique` | consommation publique, en points de PIB | M8, M11 | B, D |
| `taux_is` | taux normal de l'impôt sur les sociétés | M8 | B fragile |
| `bareme_ir` | taux et seuils du barème, décote, plafond du quotient familial | M4 (OpenFisca), M10, M8 | A, B |
| `rsa`, `prime_activite`, `allocations_familiales` | montants de base | M4, M10, M8 | A, B |
| `age_legal` | âge d'ouverture des droits | M1, M9, M8 | B, D |
| `transferts_menages` | transferts non ciblés, en points de PIB | M8, M11 | B |
| `energie_import` | choc de prix (environnement) | M5, M8 | A, B |
| `reindustrialisation` | objectif de substitution d'importations | M5, M8 | D |
| `salaires` | hausse générale ponctuelle | M8 | B |

Chaque mesure porte ses limites propres. Elles sont reproduites dans la restitution.

## 3. Contenu de la restitution

- Écarts au compte de référence pour une dizaine d'indicateurs, aux horizons 1, 3 et 7 ans, avec graphiques : PIB, emploi, chômage, prix, revenu disponible, solde et dette publics, demande, utilisation des capacités.
- Effets directs, avant bouclage macroéconomique : impôt, prestations, pensions.
- Effets par décile de niveau de vie, et ménages types (six profils fictifs calculés par OpenFisca), pour les mesures socio-fiscales.
- Rétroactions européennes : taux de la BCE, taux long français, demande des partenaires.
- Intervalles d'incertitude, si demandés.
- Fiche de transparence : mesures, hypothèses du compte de référence, données, modèles, paramètres sensibles, incertitudes, limites.

Aucune note globale n'est attribuée.

## 4. Exemples symétriques (illustratifs, non attribués à un programme)

| | A — relance : dépense +1 pt, RSA +10 %, retour à 62 ans | B — consolidation : dépense −1 pt, IS 20 %, barème non revalorisé, 65 ans |
|---|---|---|
| PIB 2024 / 2026 / 2030 | +1,30 % / +0,45 % / −0,62 % | −1,39 % / −0,61 % / −0,04 % |
| Chômage 2026 | −1,4 pt | +0,8 pt |
| Prix à la consommation 2030 | +2,8 % | −1,2 % |
| Solde public 2026 / 2030 | −0,76 / −1,17 pt | −0,02 / +0,17 pt |
| Dette 2030 | +1,7 pt | +1,6 pt |
| Effet direct | RSA : +1,9 Md€ versés ; 1er décile +163 €/UC/an | impôt sur le revenu : +2,7 Md€ ; 10e décile −174 €/UC/an |
| Temps de calcul | 233 s | 148 s |

**Lecture.**
- **Scénario B** : la baisse de la dépense améliore le solde public, mais la baisse de l'IS et le bouclage macroéconomique effacent l'essentiel de ce gain. La dette augmente aussi, faute de croissance nominale.
- **Scénario A** : il réduit nettement le chômage. Le retour à 62 ans retire des actifs, ce qui tend le marché du travail et fait monter prix et salaires. Il détériore le solde public.

Ces résultats illustrent la mécanique et doivent être lus avec leurs incertitudes (`07_validation_integrale.md`).

## 5. Performance et architecture

- **Temps de calcul.**
  - Chargement et estimation du modèle : environ 30 s, une fois par processus.
  - Simulation bouclée : 3 à 5 s par trajectoire, environ 20 s avec le couplage européen.
  - Mesure socio-fiscale : 2 à 5 minutes au premier calcul (OpenFisca sur 2 % des ménages, environ 3 Go de mémoire), puis mise en cache.
  - Profils types : environ 30 s.
- **Pour un service public**, il faudrait :
  - précalculer les variantes élémentaires (mesures paramétriques sur une grille de valeurs), pour des réponses en quelques secondes ;
  - placer la microsimulation dans une file d'attente de calculs ;
  - conserver chaque simulation (scénario, version du modèle, empreintes des données) pour qu'elle reste reproductible.

## 6. Reste à faire avant une ouverture au public

1. Interface web : composition de scénario, affichage des résultats, comparaison de scénarios. Le format JSON et la page de restitution en sont la base.
2. Élargir le catalogue : TVA, CSG, cotisations, investissement public, emploi public, dépenses par fonction, énergie et climat, logement.
3. Effets distributifs complets : CSG, cotisations, TVA par décile.
4. Revue scientifique externe des modèles et du catalogue (cahier des charges, phase 7), avant toute diffusion.
5. Versionnement des résultats et des données, et suivi des révisions des sources.
