# 26 — Documentation scientifique du modèle (état au 24 novembre 2026)

Document de synthèse : il rassemble, dans un ordre de lecture, ce qui est dispersé dans les documents de module
(M1-M25) et de phase (07-22), et renvoie à eux pour le détail des estimations. Configuration documentée : **P4**
(environnement de travail de la phase 5) ; **v0.9** reste la configuration reproductible par défaut, **v0.8** la
référence historique immuable (branche `main`).

Conventions de statut, utilisées partout :
**[D]** donnée observée ou règle publiée ; **[E]** paramètre estimé par le projet ; **[C]** calibré sur la
littérature ou sur une cible ; **[H]** hypothèse de modélisation ou de scénario ; **[X]** exploratoire.
Échelle de confiance du registre (doc 20) : A (estimé sur données françaises, diagnostics satisfaisants), B (estimé ou
repris d'études causales proches), C (littérature sans estimation propre), D (hypothèse), X (exploratoire).

---

## 1. Objet, nature et périmètre

Modèle macroéconomique annuel de la France, multisectoriel (tableau entrées-sorties à 64 produits, 25 branches
marchandes), de type néo-keynésien à correction d'erreur : la demande détermine l'activité à court terme, l'offre
(fonction de production CES, population active, chômage structurel) la détermine à moyen terme par une fermeture
explicite. Il est couplé à une microsimulation statique des ménages (OpenFisca-France) pour les mesures
socio-fiscales et à des modules de comportements (offre de travail, hauts revenus, retraites). Horizon de projection :
2047. Objet : comparer des programmes de politique économique, effet = Y(environnement, régime, programme) −
Y(environnement, régime, programme nul).

Familles de modèles de référence dont il s'inspire : modèles macroéconométriques institutionnels français (Mésange
de l'Insee et de la DG Trésor, Emma, FR-BDF de la Banque de France pour le bloc d'anticipations et de politique
monétaire, ThreeME de l'OFCE-ADEME pour la structure multisectorielle). Différences assumées : données ouvertes
seulement, estimation plus parcimonieuse, modules de microsimulation intégrés, séparation explicite environnement /
régime / programme.

## 2. Architecture

| Couche | Modules | Rôle |
|---|---|---|
| Données et comptes | M1 démographie, M3 cadre comptable, M5 TES et prix de Leontief | population, comptes de secteurs, structure productive |
| Ménages (micro) | M4 population et OpenFisca, M10 couplage, M14 hétérogénéité, M16 distribution dynamique | impôts et prestations ménage par ménage, propensions par décile |
| Comportements | M7 équations estimées, M13 comportements, M15 offre de travail, M9 retraites | emploi, prix, salaires, demande, commerce ; réponses fiscales ; activité des seniors |
| Cœur | M8 (+ M17 dette par cohortes, M18 prix, M19 salaires, M21 compte des sociétés) | résolution annuelle par point fixe, fermeture, finances publiques, comptes d'agents |
| Référence | M8_reference | trajectoire à politique inchangée, calage 2023-2025, FMI 2026-2031, COR au-delà |
| Europe et monnaie | M11 (zone euro, ancien bloc), M24 politique monétaire et conditions financières | règle de la BCE, Bund, prime souveraine, taux des crédits |
| Incertitude, validation | M12, M22 | variantes de paramètres, validation prédictive |
| Régimes et programmes | M23 régimes, M25 pont programmes, M26 contraintes européennes, M27 corpus | moteur d'évaluation |
| Interface | simulateur/ (catalogue des mesures, curseurs, exécution) | traduction des mesures en exogènes |

Résolution (M8) : chaque année, point fixe amorti (≤ 60 itérations, amortissement 0,5, critère 1e-7) sur la
production, les salaires et le chômage, dans l'ordre : prix d'importation → salaires, prix de VA, prix de Leontief →
emploi et investissement par branche → revenu disponible et demande → importations et production. Puis potentiel,
finances publiques, compte des sociétés (rétroaction par variables retardées). Les régimes (M23-M24) agissent par un
crochet en début d'année n'utilisant que les années passées.

## 3. Équations (configuration P4)

### 3.1 Offre, emploi, fermeture

- **Emploi marchand** (25 branches), demande de travail CES en heures à production donnée :
  ln N = ln q − σ ln(c_h / p_va) − (1 − σ)(ln E + ln d) ; σ = 0,45 [C, non identifié ; environnements 0,3 et 0,6
  calibrés en lot 5.3] ; tendance d'efficience E dérivée de la même condition sur 8 ans.
- **Emploi non marchand** par sous-branche : VA en volume / productivité tendancielle propre [D/C].
- **Potentiel** : CES normalisée sur la VA marchande + VA non marchande ; α = 0,35 [A].
- **Chômage** : population active (M1, M9, M15) − emploi ; loi d'Okun dans les sorties [E].
- **Fermeture d'offre** : un supplément de demande résorbe chaque année ρ = 0,2 de l'écart de production [B] et
  anticipe les révisions du potentiel (θ = 0,75) [C] ; elle représente les canaux non modélisés (confiance, crédit,
  politique monétaire avant M24). Variantes : ρ = 0,1 / 0,3 ; mode « chômage » (M23 `JEUX_PARAMETRES`).

### 3.2 Prix, salaires, marges

- **Prix de VA** (panel de 25 branches, correction d'erreur) vers la frontière des prix de facteurs :
  ln p_va* = θ_b ln CSU + (1 − θ_b) ln(p_I K_{t−1} / q), θ_b part du travail de la branche [D] ; dynamique de court
  terme sur le CSU et le volume [E] ; pente sur l'écart de production κ = 0,10 hors industrie [C].
  Variante : équation v0.9 (environnement `p4_prix_v09`).
- **Prix de production et à la consommation** : système de Leontief (prix de VA, prix d'importation par produit avec
  transmission θ estimée [E], impôts sur les produits [D]).
- **Salaires** : indexation de court terme 0,39 sur les prix à la consommation [E], correction d'erreur vers la part des
  salaires [E], Phillips −0,004 par point d'écart de chômage [C, non identifié], rigidité à la baisse ×0,5 [C].
- **Coût du travail** = rémunérations − subventions sur salaires (CICE 2013-2018) [D].

### 3.3 Demande

- **Consommation** : correction d'erreur sur le revenu disponible réel [E] ; épargne de précaution ψ_u = 0,3 % par
  point de chômage [C] ; effet du taux réel ψ_r = 0,2 [C], le taux étant depuis le lot 5.2 le taux des crédits aux
  ménages de M24 ; propensions marginales par décile pour les mesures (M14) [E/C].
- **Logement** : équation estimée sur le revenu disponible [E].
- **Investissement des branches** : accélérateur en correction d'erreur [E] ; coût d'usage avec le taux des crédits
  aux sociétés (M24) et l'IS [C] ; canal de trésorerie 0,10 [C].
- **Exportations** : demande mondiale et compétitivité-prix [E] ; **importations** : demande pondérée par les contenus
  en importations, prix relatifs, tendance [E].

### 3.4 Compte des sociétés (M21)

Intérêts versés = taux apparent × dette, le taux apparent rejoignant le taux de marché (pondération 0,77 court /
0,23 long, transmission 1,29, écart 3,42 pt) à la vitesse μ = 0,60 [E, 1999-2024] ; intérêts reçus = 0,77 × versés [C] ;
IS = taux apparent × résultat courant × facteur fiscal [D/C] ; dividendes = 0,364 × résultat de t − 1 [C]
(ménages 42 %, reste du monde 50 %, APU 8 % [D]) ; dette des SNF = dette de base indexée + φ = 1,06 × cumul des
écarts de besoin de financement [E].

### 3.5 Finances publiques

Recettes : taux apparents sur assiettes simulées [D/E] ; IS par M21. Dépenses : rémunérations (salaire public instrument
× emploi), consommation en volume × prix, prestations indexées sur les prix de t − 1, chômage ∝ chômeurs, autres en
part du PIB. Charge d'intérêts par cohortes d'émission (M17, courbe des taux, indexées ; validée sur l'AFT) [D/E].
Convention de dépense de la référence (phase 5) : consommation publique et prestations hors pensions à part constante
du PIB potentiel conventionnel (population active × (1 − u*) × productivité 0,7 %) [H].

### 3.6 Politique monétaire et conditions financières (M24)

En écart à la référence (années ≥ 2027, informations de t − 1) :
- BCE : Δi_t = 0,728 Δi_{t−1} + 0,393 Δπ^{ZE}_{t−1} + 0,302 Δy^{ZE}_{t−1} [E ; forme contemporaine estimée appliquée à
  t − 1, la forme retardée ayant un signe erroné] ; π et y de la zone = poids de la France × écart français + chocs du
  reste de la zone.
- Bund : ΔB_t = ΔB_{t−1} + 0,386 (Δi_t − Δi_{t−1}) [E] (variante : anticipations rationnelles sous la règle).
- Écart souverain : chocs + 0,013 × Δdette/PIB − 0,0148 × Δsolde/PIB [E, panel zone euro à effets fixes hors
  2010-2013 ; avec la crise : 0,0122 et −0,118] ; OAT = Bund + écart.
- Crédits nouveaux, ajustement partiel : ménages vitesse 0,429, transmission de long terme 0,896 ; sociétés vitesse
  0,926, 0,780 [E, séries MIR de la BCE].
- Taux court de référence : Euribor observé (2,63 % en octobre 2026) à partir de 2027 [D].

### 3.7 Régimes budgétaires (M23)

Solde stabilisant s̄ = (r̄ − ḡ)/(1 + ḡ) · d ; cible R2 = s̄ + β (d − d*) ; effort Δe = clip(α (s* − s), 0 ou −plafond,
plafond) ; clause de sauvegarde si écart de production < −1,5 ; instruments répartis (consommation publique,
prestations, impôts des ménages, impôts sur les produits). Valeurs centrales α = 0,5, β = 0,02, d* = 90 %, plafond
0,5 point [H, décision du 24 novembre 2026]. Modes « figé » (effort de la référence) et « actif » (réaction au
programme).

### 3.8 Ménages (micro) et comportements

- M4 : population de 2 % des ménages construite à partir du recensement 2022 et des tableaux DGFiP, IR calculé par
  OpenFisca, prestations sur deux sous-échantillons de 0,5 % ; recours apparent en masse (RSA 0,68, prime d'activité
  0,66) [D/E].
- M13 : réponses des hauts revenus et des patrimoines (élasticités du revenu imposable 0,2, du capital 0,5, mobilité
  0,15 ; ISF : pertes 25 % puis 35 % à 5 ans ; successions 10 %) [C, fourchettes basse/haute].
- M15 : offre de travail (participation 0,2, heures 0,1) [B].
- M9 : pensions par génération, activité des seniors estimée (âge légal) [B] ; pas de durée d'assurance.
- M16 : distribution dynamique (transitions emploi-chômage en espérance) [C].

### 3.9 Contraintes européennes (M26)

Qualification des mesures (niveaux 0-4), variantes conforme / contentieux / tension, amendes PDE (0,05 % du PIB par
semestre au plus) [D], prime souveraine (M24) [E] et chocs [H]. Voir doc 24.

## 4. Données

Toutes ouvertes (décision A7), téléchargées par script, empreintes SHA-256 (doc 02) : Insee (comptes nationaux
annuels et trimestriels, TES, projections de population 2026, recensement 2022), Eurostat (comptes de secteurs,
bilans, dette de Maastricht, activité), DGFiP (IRCOM, déclarations 2042, déciles), DREES, AFT (dette), BCE (taux MIR,
taux directeurs, rendements), FMI (WEO et millésimes pour la validation ex ante), AMECO, COR (hypothèses de long
terme), OpenFisca-France (législation). Données indisponibles et substitutions : doc 20, section finale (potentiel
en temps réel, patrimoine par ménage, héritages, transitions individuelles, crise sanitaire).

## 5. Méthodes d'estimation et de calibration

| Bloc | Méthode | Échantillon | Remarques |
|---|---|---|---|
| Équations de comportement (M7) | MCO en correction d'erreur (Engle-Granger, une étape), effets fixes de branche pour les panels | 1997-2019 hors Covid | tests de stabilité et rétrosimulations équation par équation |
| Fermeture (ρ, θ) | inférence indirecte (durée des écarts de production) | AMECO, FMI 1982-2019 | doc 19 |
| Compte des sociétés | MCO, ratios observés | 1997-2024 | Lintner non identifié → règle proportionnelle |
| Règle BCE, Bund, crédits | MCO sur séries annuelles de la zone euro | 1999-2025 | forme contemporaine |
| Prime souveraine | panel zone euro, effets fixes | hors 2010-2013 (variante avec) | coefficient de solde fragile |
| Paramètres non identifiés (σ, Phillips, κ, ψ) | calibration sur la littérature + jeux de sensibilité | — | jamais forcés par l'estimation |
| Référence | calage des constantes de branche sur les résidus moyens récents, cibles FMI et COR | 2023-2031 | revalidation par empreinte des paramètres |

Règle de méthode : pas de calibration pour améliorer une simulation particulière ; une spécification n'est pas
retenue sur le seul critère de l'erreur quadratique ; tout paramètre non identifié reçoit une valeur centrale
documentée et des variantes.

## 6. Tests

| Niveau | Contenu | Résultat principal | Références |
|---|---|---|---|
| Identités comptables | 142 contrôles d'intégration (comptes d'agents, TES, dette-solde) | 142/142 | doc 21 §8 |
| Rétrosimulation conditionnelle | modèle complet sur 2000-2019 aux exogènes observées | erreurs documentées par variable | doc 21 §5.1 |
| Ex ante (millésimes FMI) | prévision avec les seules informations d'époque | croissance meilleure que le FMI ; dette biaisée à la hausse (législation inchangée) | doc 21 §5.3 |
| Choc identifié (CICE) | 71 000 emplois en 2016 contre ≈ 100 000 dans les évaluations ex post | ordre de grandeur correct, plutôt bas | doc 21 §5.4 |
| Reproduction | v0.8, v0.9, référence R0 à l'identique | exacte | tests/test_phase5.py |
| Additivité des mesures | somme des effets isolés vs effet joint | documentée | resultats/validation_additivite.md |
| Robustesse | 10 régimes × 3 horizons pour S1-S5 ; sensibilités structurelles ; environnements σ et prix | voir doc 23 | phase5/resultats |
| Revalidation du cache | empreinte de tous les paramètres calibrés et de ~70 trajectoires de contrôle | refuse un coefficient modifié | tests/test_lot53.py |
| Phase 6 et corpus | intégrité du corpus, recoupement des totaux publiés, conversions, variantes européennes | 6/6 | tests/test_phase6.py |

Échecs connus et documentés de la suite v0.8 : `test_offre_travail_heterogene` (clés obsolètes),
`test_choc_de_productivite_defavorable` (signe de la dette dans la référence explosive). Non corrigés : ils portent
sur des configurations historiques conservées telles quelles.

## 7. Paramètres hypothétiques principaux et sensibilité

Classement d'influence sur les effets de programmes (doc 21 §7.2, lot 5.3) : fermeture (ρ, mode), σ, pente de Phillips
et ancrage, semi-élasticité de l'IS aux bénéfices, transmission monétaire et prime souveraine, propensions des hauts
revenus, effets de l'assurance chômage sur u*. Chacun a un jeu de variantes nommé (M23 `JEUX_PARAMETRES`,
`STRUCTURELS`) utilisable sans recalibration ; σ et l'équation de prix ont des environnements calibrés propres.

## 8. Limites

1. **Pas trimestriel non implémenté** (décision du lot 5.3 : non justifié pour la comparaison de programmes
   annuels, doc 23).
2. **Transmission monétaire faible** vers l'activité (vigilance) ; marché du logement et canal bancaire non modélisés.
3. **Écart de chômage** environ 2,5 fois plus réactif que ne l'impliquerait la loi d'Okun dans certains chocs
   (vigilance).
4. **Référence à politique inchangée explosive** (dette 274 % du PIB en 2047 avec la convention de part constante) :
   les effets des programmes se lisent en écart et sous règle budgétaire.
5. **Microsimulation statique** : revenus de 2024 indexés ; pas de retour macro → micro.
6. **Retraites** : pas de durée d'assurance, décote, surcote, carrières longues, ni capitalisation.
7. **Commerce extérieur** : pas de change, pas de modèle du reste de la zone euro au-delà des chocs exogènes.
8. **Énergie** : pas de distinction des taux de TVA par produit énergétique ni de substitution entre énergies.
9. **Qualité des services publics, santé, éducation** : effets de long terme non représentés (sauf capital public et
   R&D, exploratoires).
10. **Anticipations** : adaptatives partout sauf option sur le Bund ; pas d'effet de crédibilité des règles budgétaires.

## 9. Modèles alternatifs (pour la discussion des résultats)

| Alternative | Ce qu'elle changerait | Où elle est approchée dans le projet |
|---|---|---|
| DSGE à anticipations rationnelles (type FR-BDF, QUEST) | effets d'annonce, crédibilité, éviction par les taux | option d'anticipations rationnelles sur le Bund ; fermeture rapide |
| Modèle à offre déterminante (néoclassique) | multiplicateurs faibles, effets d'offre dominants à moyen terme | fermeture rapide (ρ = 0,3), variante chômage |
| Stock-flux cohérent (post-keynésien) | rôle des bilans et du crédit | compte des sociétés, dette des SNF ; pas de bilans complets des ménages |
| Microsimulation dynamique (Destinie, Prisme) | retraites par carrière | M9 simplifié |
| Équilibre général calculable multisectoriel (ThreeME) | prix relatifs, énergie | TES et prix de Leontief, sans substitution énergétique |

## 10. Mécanismes sous-représentés : liste priorisée

Priorité selon (i) l'enjeu dans le corpus des programmes 2027 (doc 25) et (ii) la sensibilité des résultats.

| Priorité | Mécanisme | Mesures concernées | État | Effort | Recommandation avant le rapport |
|---|---|---|---|---|---|
| 1 | Paramètres des réformes de retraites : durée d'assurance, carrières longues, décote/surcote | P08 (62 ans, 42 annuités, carrières longues), H05 (65 ans, 45 annuités, départs précoces), L34/L36 | âge seul (M9) | moyen | **oui** : écart majeur entre les trois programmes ; à défaut, présenter les coûts annoncés à côté des coûts M9 |
| 2 | Piliers de capitalisation (cotisations réorientées) | P08, H05 | canal disponible (recettes sans effet de demande, négatives) sans montant publié | faible | documenter la correspondance ; simuler dès que les flux sont publiés |
| 3 | Investissement hors APU (pôle public bancaire) : financement, dette, effet d'offre, additionnalité | L33 (100 Md€/an) | effet de demande ajouté (lot 6) | moyen | variantes d'additionnalité (100 / 50 / 25 %) dans le rapport |
| 4 | TVA et prix de l'énergie par produit | P10, L25 | taux normal équivalent | moyen | **oui** si P10 reste central : bloc énergie du TES (produits C19, D35) |
| 5 | Durée d'indemnisation du chômage et retour à l'emploi (RSA) | H07, H08, L35 | montants seulement | moyen | variantes d'effet sur u* |
| 6 | Composition des économies non ventilées (immigration, État, social) | P03, P05, H01 | hypothèses de composition | faible | variantes de composition + lecture « régime » |
| 7 | Heures supplémentaires et durée du travail à la hausse | H06 | curseur symétrique calé sur la baisse des 35 heures | moyen | variante d'élasticité de la production aux heures |
| 8 | Crédibilité des règles d'or (prime souveraine) | P02, H02 | non représentée | faible | variante de prime réduite sous règle active |
| 9 | Effets de richesse et de taux sur l'immobilier | ISF, successions, taux | absents | élevé | non |
| 10 | Pas trimestriel | calendrier infra-annuel | non | élevé | non (doc 23) |
