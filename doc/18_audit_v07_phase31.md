# 18 — Audit de la version 0.7 (phase 3.1, objectif v0.8)

Statut : audit préalable aux modifications. Chaque limite est décrite (mécanisme implémenté, hypothèses implicites,
conséquences, nature du problème), puis plusieurs corrections sont comparées. Les chiffres cités proviennent de
simulations exécutées (scripts indiqués). Les corrections retenues sont décrites dans le document 19.

## 0. Défaut de code découvert pendant l'audit

**Mécanisme.** Dans `Modele.simuler`, l'argument `amorti` (0,5) règle l'amortissement de la résolution par point fixe
de chaque année. En v0.7, la fermeture sur l'écart de production utilisait une variable locale du même nom pour son
terme proportionnel (0,3). Dès la première année résolue avec la nouvelle fermeture, l'amortissement du point fixe
passait donc de 0,5 à 0,3.

**Conséquence.** Lorsque la résolution converge (seuil 10⁻⁷, 60 itérations), la solution est la même et seul le temps
de calcul change. Mais les essais de la v0.7 avec un terme proportionnel nul (0) annulaient l'amortissement : la
résolution ne progressait plus, et l'« instabilité » observée qui avait conduit à retenir 0,3 était un artefact.
**Nature : informatique.** Corrigé (variable renommée) ; tous les résultats v0.7 sont recalculés en v0.8, et le choix
des paramètres de fermeture est refait (§ 2).

## 1. Distribution des effets calculée avant les effets macroéconomiques

**Mécanisme.** `m10_couplage.distribution` compare deux calculs OpenFisca (législation de base et réformée) sur les
revenus de l'année de la microsimulation. Le résultat (variation du niveau de vie par ménage) est agrégé par décile et
par groupe. Le modèle macroéconomique reçoit l'agrégat de cette variation comme choc de revenu.

**Hypothèses implicites.** Emploi, salaires, prix, revenus du patrimoine, pensions et prestations hors mesure sont
inchangés pour les ménages ; les mesures qui ne passent pas par le revenu des ménages (IS, impôts de production,
cotisations employeurs, droits de succession, dépenses publiques) ont une incidence nulle sur eux.

**Conséquences.** Une mesure qui crée des emplois ou augmente les salaires réels sous-estime les gagnants ; une mesure
inflationniste les surestime ; les prélèvements sur les entreprises semblent indolores (S1 de la v0.7 n'avait
« aucun perdant »).

**Nature : conceptuelle et de données.** Les données (échantillon de ménages du recensement apparié aux barèmes,
revenus et caractéristiques) permettent une correction.

**Options.**
| Option | Avantages | Limites | Faisabilité |
|---|---|---|---|
| A. Microsimulation dynamique complète (transitions individuelles emploi/chômage, vieillissement) | Rigoureuse | Lourde ; transitions non estimables sans panel ouvert | Faible à cet horizon |
| B. Population synthétique par cellules (décile × statut × famille), effets macro appliqués par cellule | Légère | Perd l'hétérogénéité intra-cellule, gagnants/perdants approximatifs | Bonne |
| C. Hybride : ménages de la microsimulation (≈ 41 000 ménages pondérés), chaque canal macroéconomique appliqué au revenu de chaque ménage selon ses caractéristiques (salaires, pensions, statut, consommation), probabilités d'emploi en espérance par cellule, réconciliation avec les agrégats macro | Garde l'hétérogénéité ; cohérent avec le macro ; pas de transitions à estimer | Effets d'emploi en espérance (pas de tirage) ; dépend de profils de consommation et de patrimoine par décile | Bonne |
Choix : **C**, avec contrôle de cohérence (la somme des revenus micro reproduit la variation du revenu disponible
macroéconomique).

## 2. Transmission demande-potentiel (anticipation θ)

**Mécanisme.** Supplément de demande Z_t = Z_{t−1} − ρ g_{t−1} − a (g_{t−1} − g_{t−2}) + θ (ln Y*_{t−1} − ln Y*ref_{t−1}),
avec ρ = 0,15, a = 0,3, θ = 1,5.

**Hypothèses implicites.** θ choisi par simulation (fermer l'écart d'un choc de productivité en rampe), non estimé ;
l'anticipation porte aussi sur la part du potentiel due au capital, qui est elle-même produite par la demande
(investissement) — risque de double compte ; le choix de a reposait sur le défaut du § 0.

**Conséquences.** Dette de S3 en 2047 de −9 à +43 points selon θ (1 à 2) ; oscillations de période deux ans après
un choc ponctuel ; trajectoires de long terme des stratégies d'offre peu fiables.

**Nature : statistique et conceptuelle** (le paramètre n'est pas directement observable ; l'écart de production
publié est lui-même estimé par filtrage).

**Options.**
| Option | Principe | Limite |
|---|---|---|
| A. Estimation directe par ARDL de l'écart publié sur la croissance du potentiel | Simple | Le potentiel publié est filtré sur la production : biais de simultanéité (constaté : β₀ > 0) |
| B. Inférence indirecte sur la persistance de l'écart (demi-vie) et sur la forme de la réponse à un choc d'offre (pas d'oscillation) | Utilise ce que les données identifient | Identification partielle de θ |
| C. Ancrage microéconomique : réponse de la consommation à un choc permanent de revenu (Blundell, Pistaferri, Preston 2008 : ≈ 0,6-0,65) et de l'investissement (accélérateur) | Fondé sur des estimations causales | Concerne la consommation et l'investissement, pas toute la demande |
| D. Spécifications alternatives : anticipation sur le seul potentiel exogène (hors capital), asymétrie, dépendance à l'état | Teste la structure | Données insuffisantes pour l'asymétrie |
Choix : **B + C**, avec test de **D** (asymétrie et dépendance à l'état testées sur données ; part du capital
traitée comme incertitude de structure).

## 3. Absence de backtest historique

**Mécanisme.** La v0.6 avait des rétrosimulations courtes (2-4 ans, origines 2012-2021) du seul modèle de demande ;
la v0.7 n'a pas été rétrosimulée.

**Nature : informatique (outil existant à étendre) et de données** (pas de potentiel en temps réel publié en
données ouvertes ; politiques fiscales passées à représenter).

**Options.** (A) Rétrosimulation dynamique longue (2011-2019) en temps réel (coefficients estimés jusqu'à
l'origine, potentiel extrapolé depuis l'origine), politiques observées en exogènes ; (B) rétrosimulations à
origines multiples, horizon 1-5 ans ; (C) tests par bloc (finances publiques à bases observées). Choix : **A + B + C**,
avec la crise sanitaire traitée à part (pas de mécanisme de confinement dans le modèle).

## 4. Microsimulation limitée à cinq configurations familiales (offre de travail)

**Mécanisme.** M15 calcule gains à l'emploi et taux marginaux sur cinq cas types × deux niveaux de salaire, pondérés
par le recensement. **Conséquences.** Les effets d'offre de travail ignorent l'hétérogénéité des revenus du conjoint,
du logement, des enfants. **Nature : informatique et de calcul.** **Options.** (A) Calculer les incitations sur
l'échantillon de ménages M10 (OpenFisca, variation de 1 % du salaire de chaque actif) ; (B) étendre les cas types
(statut d'occupation du logement, nombre d'enfants, revenu du conjoint) : 5 → 18 cas. Choix : **B** pour cette phase
(A dépasse le budget de calcul : plusieurs heures de calcul OpenFisca par variante).

## 5. Incidence économique de la fiscalité

**Mécanisme.** IS : base × taux, transfert de bénéfices, trésorerie ; impôts de production : 50 % répercutés sur les
prix ; cotisations employeurs : coût du travail ; droits de succession : recette sans effet. Les profits supplémentaires
sont distribués en dividendes selon M14. **Hypothèses implicites.** Aucune incidence de l'IS ou des impôts de
production sur les salaires ; incidence des cotisations employeurs entièrement sur l'employeur à long terme ; droits
de succession sans contribuable identifiable. **Conséquences.** Prélèvements sur les entreprises sans perdants parmi
les ménages. **Nature : conceptuelle et empirique.**

**Options.** (A) Partage explicite de l'incidence (actionnaires / salariés / consommateurs) par prélèvement, paramètres
de la littérature (Fuest, Peichl, Siegloch 2018 : ≈ 50 % de l'impôt local sur les entreprises supporté par les
salariés ; Bozio, Breda, Grenet 2019 : incidence des cotisations sur les salaires selon le lien avec les prestations ;
Carbonnier et al. 2019 : partage du CICE avec les salaires des plus qualifiés) ; (B) modèle d'équilibre général à
plusieurs facteurs. Choix : **A**, avec fourchettes ; l'incidence passe par les salaires et les prix du modèle
macroéconomique (pas d'imputation directe qui doublerait l'effet), puis par la distribution dynamique.

## 6. Comportements d'entreprises exploratoires

Transfert de bénéfices (L), trésorerie (L), délocalisation énergétique (L), R&D (L/X), formation (X), relocalisation
(supposée), durée du travail (hypothèse non estimée). Différences PME/grandes entreprises non représentées. Les
leviers sans estimation robuste restent exploratoires ; l'investissement à la fiscalité est confronté à
l'élasticité au coût d'usage estimée sur données françaises (équation M7) et aux évaluations du CICE.

## 7. Cohérence entre modules

Points vérifiés et à tester automatiquement : identités comptables (somme des emplois = ressources ; dette_t =
dette_{t−1} − solde ; PIB nominal = volume × prix), absence de double compte entre microsimulation et équation de
consommation (le revenu des ménages entre une seule fois), reproductibilité (deux exécutions identiques), stabilité
numérique (convergence du point fixe), monotonie des réponses aux paramètres.
