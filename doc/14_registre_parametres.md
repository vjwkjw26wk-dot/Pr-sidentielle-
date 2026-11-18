# Registre des paramètres et incertitudes (version 0.6)

Généré par tests/registre_parametres.py (fichier réutilisable : outputs/registre_parametres.csv). Catégories : **E** estimé sur données françaises ; **C** calibré sur données françaises ; **L** transposé de la littérature ; **H** hypothèse conventionnelle. Confiance pour E : élevée si |t| ≥ 3, moyenne si 2 ≤ |t| < 3, faible sinon. Une erreur-type faible ne garantit pas l'absence de biais de spécification (simultanéité, variables omises, rupture) : la confiance indiquée est statistique.

| Paramètre | Équation | Valeur | Cat. | Méthode, période (n) | Erreur-type (t) | Confiance | Plage | Dépendances |
|---|---|---|---|---|---|---|---|---|
| Consommation : élasticité de court terme au RDB réel | consommation.dlrdb | 0.8532 | E | MCO, 1997-2019 (23) | 0.2054 (4.2) | élevée | 0.442 à 1.264 (± 2 e.-t.) | multiplicateurs, toutes mesures sur les ménages |
| Consommation : force de rappel | consommation.ecart_1 | -0.2178 | E | MCO, 1997-2019 (23) | 0.2109 (-1.0) | faible | -0.640 à 0.204 (± 2 e.-t.) | effets de moyen terme, épargne |
| Importations : élasticité de court terme à la demande | importations.dld | 1.4645 | E | MCO, 1997-2019 (23) | 0.0919 (15.9) | élevée | 1.281 à 1.648 (± 2 e.-t.) | fuites, multiplicateurs, solde extérieur |
| Importations : élasticité-prix de court terme | importations.dlprel | -0.1142 | E | MCO, 1997-2019 (23) | 0.1014 (-1.1) | faible | -0.317 à 0.089 (± 2 e.-t.) | compétitivité, salaires, TVA |
| Importations : prix relatif de long terme | importations.lprel_1 | -0.1076 | E | MCO, 1997-2019 (23) | 0.0731 (-1.5) | faible | -0.254 à 0.039 (± 2 e.-t.) | compétitivité |
| Importations : rappel | importations.lm_1 | -0.661 | E | MCO, 1997-2019 (23) | 0.1495 (-4.4) | élevée | -0.960 à -0.362 (± 2 e.-t.) | dynamique des importations |
| Exportations : élasticité à la demande mondiale | exportations.dldm | 0.7112 | E | MCO, 1997-2019 (23) | 0.0944 (7.5) | élevée | 0.522 à 0.900 (± 2 e.-t.) | trajectoire de référence, Europe |
| Exportations : élasticité-prix | exportations.dlprel | -0.5947 | E | MCO, 1997-2019 (23) | 0.171 (-3.5) | élevée | -0.937 à -0.253 (± 2 e.-t.) | salaires, cotisations, prix |
| Investissement des SNF : accélérateur | investissement_snf.dlq | 1.9457 | E | MCO, 1997-2019 (23) | 0.3332 (5.8) | élevée | 1.279 à 2.612 (± 2 e.-t.) | multiplicateurs |
| Investissement des SNF : rappel | investissement_snf.ecm_1 | -0.3952 | E | MCO, 1997-2019 (23) | 0.1392 (-2.8) | moyenne | -0.674 à -0.117 (± 2 e.-t.) | investissement de moyen terme |
| Investissement des SNF : coût d'usage du capital | investissement_snf.lcu_1 | -0.0728 | E | MCO, 1997-2019 (23) | 0.0244 (-3.0) | moyenne | -0.121 à -0.024 (± 2 e.-t.) | IS, taux d'intérêt |
| Investissement par branche : accélérateur | investissement.dlq | 0.6703 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.2042 (3.3) | élevée | 0.262 à 1.079 (± 2 e.-t.) | investissement sectoriel |
| Salaires : indexation de court terme | salaires.dlpc | 0.3944 | E | MCO, 1997-2019 (23) | 0.2225 (1.8) | faible | -0.051 à 0.839 (± 2 e.-t.) | boucle prix-salaires, inflation |
| Salaires : rappel vers la part salariale | salaires.ecm_1 | -0.093 | E | MCO, 1997-2019 (23) | 0.0567 (-1.6) | faible | -0.207 à 0.020 (± 2 e.-t.) | partage de la valeur ajoutée |
| Prix de VA : transmission du coût salarial unitaire | prix_va.dlclu | 0.67 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.1128 (5.9) | élevée | 0.444 à 0.896 (± 2 e.-t.) | compétitivité, inflation, salaires |
| Prix de VA : rappel | prix_va.ecm_1 | -0.1171 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.0574 (-2.0) | moyenne | -0.232 à -0.002 (± 2 e.-t.) | marges |
| Prix de VA : tension des capacités | prix_va.tucd | 0.0015 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.0009 (1.7) | faible | -0.000 à 0.003 (± 2 e.-t.) | contraintes d'offre |
| Emploi : élasticité de court terme à la production | emploi.dlq | 0.2592 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.0435 (6.0) | élevée | 0.172 à 0.346 (± 2 e.-t.) | emploi, chômage |
| Emploi : rappel | emploi.ecm_1 | -0.2061 | E | MCO (panel 25 branches), 1997-2019 (575) | 0.0312 (-6.6) | élevée | -0.269 à -0.144 (± 2 e.-t.) | emploi de moyen terme |
| Logement des ménages : élasticité au revenu | logement.dlrdb | 1.4837 | E | MCO, 1997-2019 (23) | 0.3504 (4.2) | élevée | 0.783 à 2.185 (± 2 e.-t.) | investissement, multiplicateurs |
| Logement des ménages : rappel | logement.ecart_1 | -0.282 | E | MCO, 1997-2019 (23) | 0.2021 (-1.4) | faible | -0.686 à 0.122 (± 2 e.-t.) | investissement des ménages |
| Transmission des prix d'importation (année même) | transmission.dlpm | 0.1785 | E | MCO, 1998-2024 (27) | 0.0572 (3.1) | élevée | 0.064 à 0.293 (± 2 e.-t.) | chocs énergétiques, inflation |
| Revenus de la propriété des ménages : élasticité au PIB nominal | revenus_d4.dpibn | 0.8737 | E | MCO, 1997-2019 (23) | 0.7609 (1.1) | faible | -0.648 à 2.395 (± 2 e.-t.) | RDB |
| Revenu mixte et EBE des ménages : élasticité au PIB nominal | revenus_ebe.dpibn | 0.8897 | E | MCO, 1997-2019 (23) | 0.1904 (4.7) | élevée | 0.509 à 1.271 (± 2 e.-t.) | RDB |
| Courbe de Phillips (E.PHILLIPS) | — | -0.004 | C | calibrage, — (—) | — (—) | faible | −0,008 à −0,002 | salaires, prix, chômage, dette (effet dénominateur) |
| Élasticité de substitution capital-travail (SIGMA_TRAVAIL) | — | 0.4 | L | transposition, — (—) | — (—) | faible | 0,2 à 0,7 | emploi après choc de coût du travail |
| Fermeture d'offre (RHO_DEFAUT) | — | 0.15 | H | convention, — (—) | — (—) | faible | 0 à 0,4 | multiplicateurs de moyen terme, tous scénarios |
| Loi d'Okun (OKUN) | — | 1.5 | L | transposition, — (—) | — (—) | moyenne | 1,2 à 2 | fermeture d'offre |
| Délai de construction des capacités (DELAI_CAPACITES) | — | 2 | H | convention, — (—) | — (—) | faible | 1 à 4 ans | réindustrialisation |
| Profil des propensions à consommer par décile | — | 0,90 … 0,40 | L | transposition, — (—) | — (—) | faible | profil plat à accentué | mesures redistributives |
| Propension du dernier centile (PMC_TOP1) | — | 0.25 | L | transposition, — (—) | — (—) | faible | 0,1 à 0,5 | dividendes, ISF, PFU |
| Part distribuée des profits supplémentaires | — | 0.5 | L | transposition, — (—) | — (—) | faible | 0,3 à 0,7 | IS, impôts de production |
| Part des dividendes aux non-résidents | — | 0.3 | C | calibrage, 2022-2024 (—) | — (—) | moyenne | 0,20 à 0,50 | RNB après baisse d'IS |
| Part des dividendes résidents reçue par les ménages | — | 0.35 | C | calibrage, 2022 (—) | — (—) | faible | 0,2 à 0,5 | RDB après baisse d'IS |
| Élasticité du revenu imposable (M13) | — | 0.2 | L | transposition, — (—) | — (—) | moyenne | 0,1 à 0,4 | rendement des hausses d'IR sur les hauts revenus |
| Élasticité des revenus du capital (M13) | — | 0.5 | L | transposition, — (—) | — (—) | moyenne | 0,2 à 1 | PFU, dividendes |
| Perte d'assiette de l'ISF (M13) | — | 0.25 | L | transposition, — (—) | — (—) | faible | 0,1 à 0,5 | rendement ISF |
| Élasticité de la production au capital public | — | 0.08 | L | méta-analyse, — (—) | — (—) | moyenne | 0,04 à 0,12 | investissement public de long terme |
| Coût public d'un point de SMIC | — | 660.0 | C | calibrage, 2025 (—) | — (—) | moyenne | 500 à 800 M€ | SMIC |
| Diffusion du SMIC au salaire moyen | — | 0.11 | H | convention, — (—) | — (—) | faible | 0,05 à 0,2 | SMIC |
| Répercussion de la TVA sur les prix | — | 0.8 | L | transposition, — (—) | — (—) | moyenne | 0,6 à 1 | TVA |
| Répercussion des impôts de production | — | 0.5 | H | convention, — (—) | — (—) | faible | 0,2 à 0,8 | impôts de production |
| Compensation horaire des 32 heures | — | 0.7 | H | convention, — (—) | — (—) | faible | 0,5 à 0,9 | temps de travail |
| Coefficient de pension marginale | — | 0.55 | C | calibrage, 2025 (—) | — (—) | moyenne | 0,45 à 0,7 | âge légal |
| Taux d'épargne cible de la référence | — | 17,9 → 15,5 % | H | convention, 2025-2031 (—) | — (—) | faible | 14 à 18 % en 2031 | trajectoire de référence (niveaux), peu les écarts |
| Rétroactions zone euro (THETA_PRIME, etc.) | — | M11 | C | calibrage, — (—) | — (—) | faible | 0 à 2 × central | taux, demande des partenaires |

## Coefficients fortement corrélés (|ρ| ≥ 0,7, même équation)

Ces paires sont mal identifiées séparément : leurs effets peuvent se compenser ; les tirages statistiques conjoints (tests/contre_expertise.py) en tiennent compte, les sensibilités univariées non.

| Équation | Coefficient 1 | Coefficient 2 | ρ |
|---|---|---|---|
| consommation | dlrdb | ecart_1 | -0.82 |
| importations | lm_1 | ld_1 | -0.98 |
| exportations | dldm | dlprel | +0.86 |
| salaires | dlpc | dlprod | -0.83 |
| revenus_d4 | dpc | ecm_1 | -0.76 |
| revenus_d4 | dpc | r_1 | +0.72 |
| revenus_d4 | ecm_1 | r_1 | -0.93 |

Sources principales : voir doc/12_audit_mecanismes.md (section 8) et doc/13_contre_expertise.md.
