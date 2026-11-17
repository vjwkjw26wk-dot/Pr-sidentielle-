# Phase 8 — Préparation du simulateur (prototype 0.3, avec interface de test)

**État : prototype fonctionnel, en ligne de commande.** Un scénario décrit en JSON est exécuté par l'ensemble des
modèles (M1, M4, M8-M12). Le résultat est restitué dans un fichier JSON et dans une page HTML autonome, avec la fiche
de transparence exigée par le cahier des charges (§ 17.1).

Il n'y a pas encore de service en ligne : ni serveur, ni comptes, ni file d'attente de calculs.
Code : dossier `simulateur/`. Exemples : dossier `scenarios/`.

## 0. Interface de test (version 0.3, 17 novembre 2026)

**Changements depuis la version 0.2.** Ils répondent aux retours de l'utilisateur du 17 novembre 2026.
1. **Calendrier.**
   - Les mesures entrent en vigueur en 2028 par défaut ; l'horizon est 2032, fin du mandat.
   - Corrections : les mesures socio-fiscales s'appliquaient dès 2023, faute d'année de début ; une réforme d'âge
     légal modifiait les comportements avant son entrée en vigueur.
2. **Trajectoire sans changement de politique** (`M8_reference.md`).
   - Elle est recalée sur 2023-2025, calée sur le FMI jusqu'en 2031, pilotée par la démographie, au taux de marché
     actuel.
   - Elle est affichée en niveaux, au centre de l'interface ; les mesures s'y superposent.
3. **Retraites.**
   - Âge légal de 60 à 67 ans, avec retour progressif (3 mois par génération) ou immédiat.
   - Indexation des pensions et minimum vieillesse.
   - Nouveaux indicateurs : pensions en part du PIB, retraités pour 100 actifs.
4. **Catalogue étendu à 35 curseurs** (tableau ci-dessous).
5. **Réactions des hauts revenus et des patrimoines** (M13, `M13_comportements.md`), en fourchette.
6. **Bilan automatique.**
   - Il porte sur la trajectoire sans changement, puis sur ce que changent les mesures : activité, emploi, finances
     publiques, prix, ménages, retraites, industrie.
   - Il sépare ce qui est plutôt robuste de ce qui dépend des hypothèses.
7. **Canaux de confiance et d'anticipation** : épargne de précaution, prime de risque, climat des affaires,
   acceptabilité (part des ménages perdants).
   - Ils sont chiffrés en fourchette indicative, à partir des écarts de déficit et de dette, et ne sont pas ajoutés au
     résultat central.
   - Faute de mesure fiable, le climat des affaires n'est pas chiffré.

**Mode de calcul.**
- Chaque curseur est simulé seul par la chaîne complète, aux points de sa grille (`python3 -m simulateur.precalcul`).
- L'interface interpole entre les points (0 à la valeur actuelle) et additionne les effets. Les interactions entre
  mesures sont ignorées.
- Le calcul exact se fait en local : `python3 -m simulateur.serveur`, bouton « Calcul exact ». Il accepte le JSON
  copié depuis l'interface, au format `{"curseurs": [{"cle", "valeur"}]}`.

| Groupe | Curseurs | Traitement |
|---|---|---|
| Dépenses publiques | emplois publics ; point d'indice ; santé, éducation, défense, autres (Md€) ; investissement public | consommation publique (M8, M11) ; investissement : demande et dépense, sans effet de long terme sur la productivité |
| Impôts des ménages | taux des tranches 1 à 4 de l'IR ; revalorisation des seuils ; CSG sur l'activité et sur les pensions ; TVA (taux normal) | IR : OpenFisca ; CSG : microdonnées, assiettes calées sur les totaux nationaux ; TVA : rendement agrégé, répercussion sur les prix de 80 %, répartition selon la consommation |
| Capital et patrimoine | flat tax ; ISF ; successions ; IS | assiettes agrégées et M13 ; IS : coût d'usage (M8) |
| Entreprises et travail | cotisations patronales ; SMIC ; hausse générale des salaires ; relocalisation industrielle | coût du travail (M8) ; diffusion du SMIC : 11 % de la masse salariale (hypothèse D) |
| Prestations | RSA ; prime d'activité ; allocations familiales ; aides au logement ; minimum vieillesse ; allocations chômage ; transferts | OpenFisca, ou variation proportionnelle des montants calculés ; chômage : dépense et chômage structurel (0,1 point pour 10 %) |
| Retraites | âge légal (progressif ou immédiat) ; indexation des pensions | M9, par génération |
| Environnement | taxe carbone ; prix de l'énergie importée | prix et recettes (M8) ; tableaux entrées-sorties (M5) |

Non modélisés à ce stade : durée du travail (32 heures), droits de douane, TVA à taux réduits, logement social, mesures
réglementaires.

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

## 4. Exemples symétriques (prototype 0.2 : ancienne référence, mesures en 2024 — à refaire sur la référence 1.0)

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

1. **Interface.**
   - Comparaison de scénarios côte à côte.
   - Intervalles d'incertitude dans la page.
   - Prise en compte des interactions sans serveur local : grille croisée, ou calcul à la demande hébergé.
2. **Catalogue.** Durée du travail, droits de douane, taux réduits de TVA, logement, mesures réglementaires.
3. **Profils types.** Les étendre à la CSG, à la TVA et aux pensions.
4. **Ménages.** Distribution de la TVA et de la taxe carbone à partir des enquêtes Budget de famille, au lieu de taux
   d'épargne approchés.
5. **Trajectoire de référence.**
   - Sensibilité au taux de l'OAT.
   - Emploi industriel par branche.
   - Normes de dépense de la loi de programmation.
6. **Revue scientifique externe** des modèles et du catalogue, avant toute diffusion.
7. **Versionnement** des résultats et des données.
