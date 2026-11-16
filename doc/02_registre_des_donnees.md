# Registre des données

Toutes les sources sont ouvertes et sans habilitation (décision A7). Le téléchargement est scripté (`code/src/telechargement.py`) ; chaque fichier est identifié par son empreinte SHA-256 dans `resultats/registre_telechargements.json`.

| Fichier | Producteur, jeu | Licence | Usage | Contrôle d'intégrité |
|---|---|---|---|---|
| `insee_proj2026_00_central.xlsx` | Insee, Projections de population 2026, scénario central (page 8990852) | Licence ouverte Etalab | M1 : population de départ, hypothèses, référence | Empreinte ; réplication (test A) |
| `insee_proj2026_variantes1.zip`, `_extremes.zip`, `_combines.zip`, `_travail.zip` | Insee, 28 autres scénarios (pages 8990856, 8990858, 8990860, 8990868) | Licence ouverte | M1 : directions de variation, validation | Empreinte ; réplication |
| `insee_proj2026_hyp_mortalite.xlsx` | Insee, hypothèses de mortalité jusqu'en 2125 | Licence ouverte | M1 : extension au-delà de 2070 (non encore utilisée) | Empreinte |
| `insee_proj2026_note_technique.pdf` | Insee, note technique des hypothèses | Licence ouverte | Documentation (ajustement, migrations) | — |
| `insee_ip2108.xlsx` | Insee Première n° 2108 (juin 2026) | Licence ouverte | Contrôle des chiffres publiés | — |
| `eurostat_lfsa_argan_FR_2024.json` | Eurostat, taux d'activité par sexe et âge, 2024 | Réutilisation libre (décision 2011/833/UE) | M1 : population active | Somme de contrôle des tranches |
| `eurostat_nasa_10_nf_tr_FR.json` | Eurostat, comptes non financiers des secteurs, France, 2019-2025 | Réutilisation libre | M3 | Identités (rapport M3) |
| `eurostat_nasa_10_f_bs_FR.json` | Eurostat, bilans financiers (PFN, actifs et passifs totaux) | Réutilisation libre | M3 : stocks | Σ PFN = 0 |
| `eurostat_nasa_10_f_tr_FR.json` | Eurostat, opérations financières (B9F) | Réutilisation libre | M3 : lien flux-stocks | Écart B9 − B9F explicite |
| `eurostat_gov_10dd_edpt1_FR.json` | Eurostat, dette et déficit de Maastricht | Réutilisation libre | M3 : dette publique | Recoupé avec l'Insee (mai 2026) |
| `insee_rp2022_indreg.parquet` (650 Mo) | Insee, recensement 2022, fichier détail « Individus localisés à la région » (page 8590183), 17,5 M d'individus | Licence ouverte | M4 : ménages et foyers | Population (66,4 M) et ménages (31,0 M) reproduits |
| `insee_rp2022_varmod_indreg.csv` | Insee, dictionnaire des variables du même fichier | Licence ouverte | M4 : codage | — |
| `dgfip_ircom_2025_rev2024.zip` | DGFiP, impôt sur le revenu par collectivité territoriale (IRCOM 2025, revenus 2024), tableau national par tranche de RFR | Licence ouverte | M4 : distribution des foyers, salaires, pensions ; test de l'impôt | Total des foyers (41,6 M) et de l'impôt net (91,7 Md€) |
| Grilles de salaires et pensions (valeurs saisies dans `m4_population.py`) | Insee, salaires du secteur privé 2024 par catégorie socioprofessionnelle et sexe ; DREES, Les retraités et les retraites, édition 2025 | Licence ouverte | M4 : score latent (ordre des foyers) | — |
| OpenFisca-France 177.0.0 (PyPI) | Communauté OpenFisca | AGPL-3.0 | Lot 5 : législation | Cas types (rapport lot 5) |

Valeurs législatives de référence des cas types (indépendantes d'OpenFisca) : loi de finances pour 2026 (barème, décote 897 € / 1 483 €, 45,25 %, plafond du quotient familial 1 807 € par demi-part, abattement de 10 % plafonné à 14 555 €), revalorisations du 1er avril 2026 (RSA 651,69 €, BMAF 478,16 €), SMIC 12,02 €/h au 1er janvier 2026, taux de cotisations salariales 2026.
