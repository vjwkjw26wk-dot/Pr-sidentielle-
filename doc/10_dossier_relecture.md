# Dossier pour une relecture scientifique externe (version 0.4)

**Objet.** Préparer la relecture du modèle par des économistes indépendants avant toute diffusion publique (cahier des
charges, phase 7). Le dossier liste les choix structurants, les points fragiles connus et les questions posées aux
relecteurs. La relecture elle-même ne peut pas être conduite par l'équipe qui a construit le modèle.

**Profils de relecteurs suggérés.**
- Macroéconomètre : modèles de type Mésange, OFCE-emod ou FR-BDF.
- Spécialiste de la microsimulation : OpenFisca, Ines.
- Spécialiste des retraites : connaissance des modèles du COR, Destinie ou Pensipp.
- Spécialiste des finances publiques.
- Économiste de la fiscalité des hauts revenus et des patrimoines.

## 1. Documents à fournir

- Cahier des charges et décisions : `00_decisions.md`, `01_plan_des_lots.md`.
- Modules : `M3`, `M4`, `M5`, `M7_M8`, `M8_reference`, `M9`, `M10`, `M11`, `M13`.
- Validations : `07_validation_integrale.md`, les fichiers `resultats/validation_*.md`, et en particulier
  `validation_additivite.md`.
- Simulateur : `08_simulateur.md`. L'interface de test et le code sont dans le dépôt.

## 2. Questions posées aux relecteurs

### Bouclage macroéconomique (M7, M8)
1. **Équations à correction d'erreur.** Elles sont estimées sur 1997-2019 ; les constantes de branche sont recalées
   sur les résidus récents. La spécification de l'emploi par branche et l'élasticité de substitution calibrée à 0,4
   sont-elles acceptables ?
2. **Équation de consommation.** La version 0.5 retire la variation contemporaine du chômage, pour cause de
   simultanéité. Le multiplicateur de dépense publique passe alors à 1,2 la première année, 0,85 la deuxième et 0,6
   la cinquième.
   - Est-ce cohérent avec les références (Insee-DG Trésor : environ 0,9 la première année pour une baisse de
     dépense ; OFCE : 0,6 à 1,2) ?
   - Faut-il instrumenter plutôt que retirer cette variable ?
3. **Fermeture d'offre.** Elle passe par un correcteur intégral-proportionnel de la demande selon l'écart de chômage
   (ρ = 0,15), sans fonction de production explicite. Est-ce suffisant pour des horizons de 5 à 10 ans ?
4. **Ancrage après calage.** L'écart à l'équilibre estimé constaté en 2025 est supposé durable. Faut-il plutôt le
   résorber progressivement ? Quelle vitesse retenir ?

### Trajectoire de référence (`M8_reference.md`)
5. **Choix de la référence.** Elle est calée sur les projections macroéconomiques du FMI, alors que les finances
   publiques sont à politique inchangée. Or ces projections supposent un redressement budgétaire. Faut-il corriger
   la croissance de référence de l'effet de l'absence de redressement ?
6. **Taux de l'OAT.** Il est figé au niveau d'octobre 2026 (4,89 %). Faut-il retenir une courbe de taux à terme ?
7. **Dépenses tendancielles.** Elles suivent le rythme 2011-2019 (+1,3 % en volume pour la consommation publique,
   +1,4 % pour les prestations hors pensions). Faut-il plutôt partir des normes de la loi de programmation ?

### Ménages (M4, M10)
8. **Échantillon.** L'échantillon de 2 % des ménages est reconstitué sans données individuelles fiscales. Les écarts
   aux agrégats de la DGFiP sont-ils acceptables ? La sensibilité de l'impôt sur le revenu aux seuils est 15 à 30 %
   plus faible que les chiffrages officiels.
9. **Taux de recours.** Les taux de recours apparents sont uniformes (RSA 0,68 ; prime d'activité 0,66).

### Retraites (M9)
10. **Profil d'activité des seniors.** Sa part qui se déplace avec l'âge légal est estimée à 0,75-0,78 sur les
    réformes 2010 et 2023. Est-il raisonnable de l'extrapoler à un retour à 60 ans ?
11. **Durée d'assurance.** Les conditions de taux plein et de carrière longue ne sont pas modélisées. Quelle erreur
    cela introduit-il pour les réformes simulées ?

### Comportements (M13)
12. **Élasticités.** Les élasticités du revenu imposable (0,1-0,4) et des revenus distribués (0,2-1,0) et les pertes
    d'assiette de l'impôt sur la fortune (10-50 %) sont-elles représentatives de la littérature récente ?
13. **Grands changements.** Peut-on extrapoler ces élasticités à des changements de taux de grande ampleur ?

### Mesures stylisées (hypothèses D)
14. Les paramètres retenus sont-ils défendables ?
    - 32 heures : 70 % de la baisse de durée absorbée sans embauche.
    - Droits de douane : répercussion de 80 %, riposte stylisée.
    - SMIC : diffusion à 11 % de la masse salariale.
    - Assurance chômage : 0,1 point de chômage structurel pour 10 % de variation des allocations.
    - TVA : répercussion de 80 %.
    - Capital public : élasticité de la production de 0,08.

### Interface et restitution
15. **Neutralité.** Le bilan automatique et la séparation entre résultats « plutôt robustes » et « dépendant des
    hypothèses » respectent-ils l'exigence de neutralité ?
16. **Canaux de confiance.** Ils sont présentés hors du résultat central. Leur présentation peut-elle induire en
    erreur ?

## 3. Points fragiles déjà identifiés

- La validation rétrospective 2023-2024 n'est pas concluante pour les prix et les exportations (`07_validation_integrale.md`).
- L'emploi industriel de référence recule d'environ 1 % par an, ce qui est plausible mais incertain.
- Après 2031, la trajectoire de référence découle des hypothèses du COR.
- L'approximation additive de l'interface ignore les interactions entre mesures (`validation_additivite.md`).
- Les marges d'incertitude de l'interface reposent sur une médiane de rapports estimés sur 7 mesures représentatives.
- La redistribution du produit de la taxe carbone, les effets sur les émissions et ceux sur les loyers ne sont pas
  modélisés.
