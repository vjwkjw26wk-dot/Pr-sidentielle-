# Phase 8 — Préparation du simulateur (prototype 0.4, avec interface de test)

**État : prototype fonctionnel, en ligne de commande.** Un scénario décrit en JSON est exécuté par l'ensemble des
modèles (M1, M4, M8-M12). Le résultat est restitué dans un fichier JSON et dans une page HTML autonome, avec la fiche
de transparence exigée par le cahier des charges (§ 17.1).

Il n'y a pas encore de service public en ligne. Un serveur de calcul exact tourne en local ; sa recette de
déploiement en conteneur est prête (`09_deploiement.md`).
Code : dossier `simulateur/`. Exemples : dossier `scenarios/`.

## 0. Interface de test

### Version 0.4 (17 novembre 2026, après-midi)

1. **Crédibilité du modèle.**
   - Équation de consommation : la variation contemporaine du chômage est retirée (simultanéité). Le multiplicateur
     de dépense publique devient 1,2 la première année, 0,85 la deuxième et 0,6 la cinquième, contre 1,4 / 0,93 /
     0,55 auparavant.
   - Emploi industriel de référence : environ −1 % par an au lieu de −1,8 %. Après 2025, le terme de calage de
     l'emploi est porté par les branches hors industrie.
   - Investissement public : il a désormais un effet d'offre via le capital public (élasticité de la production 0,08,
     capital public 55 % du PIB, dépréciation 4 %).
2. **Trajectoires de comparaison au choix.**
   - Politique inchangée, avec l'OAT à 4,9 %, à 3,9 % ou à 5,9 %.
   - Redressement d'ampleur FMI : effort ex ante égal à l'écart avec le solde du FMI (environ 4 points de PIB en
     2031), moitié dépenses, moitié impôts. Selon le modèle, cet effort ne réduit le déficit de 2031 que d'environ
     2,3 points, car l'activité recule (PIB −2,8 %, chômage +2,3 points en 2031).
3. **Nouvelles mesures** : durée légale du travail, droits de douane hors UE (avec riposte), taux réduits de TVA,
   logements sociaux. Le catalogue compte 39 curseurs.
4. **Ménages.**
   - La TVA et la taxe carbone sont réparties selon la structure de consommation par quintile (enquête Budget des
     familles 2015 et taux d'épargne par quintile, Eurostat).
   - Les ménages types intègrent la CSG, la TVA, la taxe carbone, l'indexation des pensions et les aides au logement.
5. **Interface.**
   - Comparaison de trois scénarios enregistrés (table et graphique).
   - Lien de partage, qui encode les curseurs et la trajectoire de comparaison.
   - Marges d'incertitude à 90 %, estimées par Monte-Carlo sur 7 mesures représentatives
     (`simulateur/incertitude_variantes.py`).
   - Bouton de calcul exact, actif dès qu'un serveur répond.
6. **Reproductibilité.** Chaque résultat porte la version du modèle et les empreintes du code et des données.
   - Serveur : points d'accès `/sante` et `/api/executer`.
   - Déploiement par conteneur : `09_deploiement.md`.
   - Dossier de relecture externe : `10_dossier_relecture.md`.
   - Validation de l'approximation additive : `resultats/validation_additivite.md`.

### Version 0.3 (17 novembre 2026, matin)

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
| Dépenses publiques | emplois publics ; point d'indice ; santé, éducation, défense, autres (Md€) ; investissement public | consommation publique (M8, M11) ; investissement : demande, dépense et effet d'offre du capital public (v0.4) ; logements sociaux (v0.4) |
| Impôts des ménages | taux des tranches 1 à 4 de l'IR ; revalorisation des seuils ; CSG sur l'activité et sur les pensions ; TVA (taux normal ; taux réduits en v0.4) | IR : OpenFisca ; CSG : microdonnées, assiettes calées sur les totaux nationaux ; TVA : rendement agrégé, répercussion sur les prix de 80 %, répartition selon la consommation |
| Capital et patrimoine | flat tax ; ISF ; successions ; IS | assiettes agrégées et M13 ; IS : coût d'usage (M8) |
| Entreprises et travail | cotisations patronales ; SMIC ; hausse générale des salaires ; relocalisation industrielle ; durée légale du travail (v0.4) ; droits de douane hors UE (v0.4) | coût du travail (M8) ; diffusion du SMIC : 11 % de la masse salariale (hypothèse D) ; durée du travail : 70 % de la baisse absorbée sans embauche (D) ; douanes : prix d'importation et riposte stylisée (D) |
| Prestations | RSA ; prime d'activité ; allocations familiales ; aides au logement ; minimum vieillesse ; allocations chômage ; transferts | OpenFisca, ou variation proportionnelle des montants calculés ; chômage : dépense et chômage structurel (0,1 point pour 10 %) |
| Retraites | âge légal (progressif ou immédiat) ; indexation des pensions | M9, par génération |
| Environnement | taxe carbone ; prix de l'énergie importée | prix et recettes (M8) ; tableaux entrées-sorties (M5) |

Non modélisés à ce stade : mesures réglementaires (normes, droit du travail, urbanisme), politique migratoire,
fiscalité locale, dépenses par fonction avec des effets propres (santé, éducation).

## 1. Utilisation

```
python3 -m simulateur.executer scenarios/exemple_A_relance.json
→ outputs/exemple_A_relance_resultats.json et .html
```

Format du scénario :

```json
{"nom": "...", "description": "...", "horizon": 2032,
 "hypotheses": {"fermeture_offre": 0.15, "europe": true, "incertitude": 0, "profils": true, "reference": "inchangee"},
 "mesures": [{"type": "depense_publique", "parametres": {"points_pib": 1.0, "debut": 2028}}, ...]}
```

ou, depuis l'interface (bouton « Copier le scénario ») :

```json
{"horizon": 2032, "hypotheses": {...}, "curseurs": [{"cle": "sante", "valeur": 10}, {"cle": "age_legal", "valeur": 62}]}
```

`incertitude` donne le nombre de tirages Monte-Carlo (0 = aucun ; 20 à 40 recommandés ; 15 à 60 s par tirage).
`reference` : `inchangee`, `oat_bas`, `oat_haut` ou `redressement` (voir `M8_reference.md`).

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
| `csg`, `tva`, `tva_reduite`, `taxe_carbone`, `pfu`, `isf`, `successions` | prélèvements (v0.3-0.4) | M10 (microdonnées), M8, M13 | A à D selon la mesure |
| `cotisations_employeurs`, `smic`, `temps_travail`, `droits_douane` | travail et commerce (v0.3-0.4) | M8 | B, D |
| `depense_fonction`, `emploi_public`, `point_indice`, `investissement_public`, `logements_sociaux` | dépenses (v0.3-0.4) | M8, M11 | B, D |
| `aides_logement`, `minimum_vieillesse`, `assurance_chomage`, `indexation_pensions` | prestations et pensions (v0.3) | M4, M9, M10, M8 | A, B, D |

Chaque mesure porte ses limites propres (`catalogue.MESURES`). Elles sont reproduites dans la restitution.

## 3. Contenu de la restitution

- Écarts au compte de référence pour une dizaine d'indicateurs, aux horizons 1, 3 et 7 ans, avec graphiques : PIB, emploi, chômage, prix, revenu disponible, solde et dette publics, demande, utilisation des capacités.
- Effets directs, avant bouclage macroéconomique : impôt, prestations, pensions.
- Effets par décile de niveau de vie, et ménages types (six profils fictifs calculés par OpenFisca), pour les mesures socio-fiscales.
- Rétroactions européennes : taux de la BCE, taux long français, demande des partenaires.
- Intervalles d'incertitude, si demandés.
- Fiche de transparence : mesures, hypothèses du compte de référence, données, modèles, paramètres sensibles, incertitudes, limites.

Aucune note globale n'est attribuée.

## 4. Exemples symétriques (version 0.4 : référence recalée, mesures en 2028, 20 tirages d'incertitude)

| | A — relance : dépense +1 pt, RSA +10 %, âge légal 62 ans (progressif) | B — consolidation : dépense −1 pt, IS 20 %, barème non revalorisé, âge légal 65 ans |
|---|---|---|
| PIB 2028 / 2030 / 2032 | +1,35 % / +0,41 % / −0,36 % | −1,21 % / −0,54 % / −0,34 % |
| Intervalle à 90 % du PIB en 2032 | −1,24 à +0,02 % | −0,45 à +0,17 % |
| Chômage 2028 / 2032 | −1,9 / −2,3 pt | +1,0 / +0,7 pt |
| Prix à la consommation 2032 | +2,4 % | −1,1 % |
| Solde public 2028 / 2032 | −0,60 / −1,07 pt | −0,03 / +0,18 pt |
| Dette 2032 | +0,6 pt (intervalle −6,5 à +2,8) | +2,2 pt (intervalle +1,0 à +5,5) |
| Effet direct | RSA : +1,9 Md€ versés ; 1er décile +163 €/UC/an | impôt sur le revenu : +2,7 Md€ ; 10e décile −174 €/UC/an |
| Temps de calcul (avec incertitude) | 21 min | 22 min |

**Lecture.**
- **Scénario A.**
  - Il soutient l'activité à court terme.
  - Le retour progressif à 62 ans réduit la population active, ce qui abaisse nettement le chômage, tend le marché du
    travail et fait monter prix et salaires.
  - À la fin du mandat, le PIB est légèrement inférieur à la référence et le déficit plus élevé d'un point.
  - La dette ne monte guère, sous l'effet de l'inflation.
- **Scénario B.**
  - Il pèse sur l'activité à court terme.
  - L'amélioration du solde est faible : la baisse de l'IS et le bouclage macroéconomique effacent l'essentiel du gain.
  - La dette augmente faute de croissance nominale.
- **Dans les deux cas**, les effets sur la dette en fin de mandat sont très incertains (larges intervalles).

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

1. **Relecture scientifique externe** (`10_dossier_relecture.md`). Elle ne peut pas être conduite par l'équipe qui a
   construit le modèle.
2. **Mise en ligne d'un service public de calcul exact** (`09_deploiement.md`) : hébergement, file d'attente, cache des
   scénarios. Il faut un serveur et une décision du porteur du projet.
3. **Incertitude propre à chaque mesure**, au lieu d'un rapport médian commun.
4. **Compléments de modélisation** :
   - normes de dépense de la loi de programmation ;
   - courbe de taux à terme ;
   - effets propres des dépenses de santé et d'éducation ;
   - émissions de gaz à effet de serre ;
   - loyers.
5. **Validation distributive** : comparaison avec l'enquête Revenus fiscaux et sociaux ; exécution croisée de variantes
   publiées par Mésange et l'OFCE.
