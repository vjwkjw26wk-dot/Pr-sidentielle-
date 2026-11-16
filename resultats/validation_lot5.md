# Lot 5 — OpenFisca-France sur cas types

OpenFisca-France 177.0.0 ; OpenFisca-Core 46.0.1. Valeurs attendues recalculées indépendamment (`tests/validation_lot5_cas_types.py`).

| Cas | Attendu | OpenFisca | Écart | Tolérance | Résultat | Source de l'attendu |
|---|---|---|---|---|---|---|
| IR revenus 2025, célibataire, RNI 15 000 € | 0.00 | -0.00 | -0.00 | 1.0 | conforme | LF 2026 art. 4 (barème, décote, plafond de l'abattement de 10 %) |
| IR revenus 2025, célibataire, RNI 20 000 € | 445.00 | 445.00 | +0.00 | 1.0 | conforme | LF 2026 art. 4 (barème, décote, plafond de l'abattement de 10 %) |
| IR revenus 2025, célibataire, RNI 30 000 € | 2104.00 | 2104.00 | +0.00 | 1.0 | conforme | LF 2026 art. 4 (barème, décote, plafond de l'abattement de 10 %) |
| IR revenus 2025, célibataire, RNI 250 000 € | 89024.00 | 89024.00 | +0.00 | 1.0 | conforme | LF 2026 art. 4 (barème, décote, plafond de l'abattement de 10 %) |
| IR revenus 2025, couple, 2 enfants, RNI 60 000 € | 2543.00 | 2543.00 | +0.00 | 1.0 | conforme | LF 2026 (barème, plafonnement QF, décote) |
| IR revenus 2025, couple, 3 enfants, RNI 150 000 € (plafonnement du QF) | 23980.00 | 23980.00 | +0.00 | 1.0 | conforme | LF 2026 |
| Salaire net, SMIC temps plein, février 2026 | 1443.14 | 1443.14 | -0.00 | 0.5 | conforme | SMIC 12,02 €/h (janv. 2026) ; taux de cotisations 2026 |
| RSA, personne seule sans ressources ni aide au logement, mai 2026 | 651.69 | 651.69 | +0.00 | 0.5 | conforme | Revalorisation du 1er avril 2026 |
| RSA, personne seule, salaire net 500 €/mois depuis 3 mois, mai 2026 | 151.69 | 151.69 | -0.00 | 1.0 | conforme | Montant forfaitaire − revenus d'activité |
| Allocations familiales, 2 enfants, revenus modestes, mai 2026 (avant CRDS) | 153.01 | 153.01 | -0.00 | 0.05 | conforme | 32 % de la BMAF (478,16 €) |
| Allocations familiales, 3 enfants, revenus modestes, mai 2026 (avant CRDS) | 349.06 | 349.06 | +0.00 | 0.05 | conforme | 73 % de la BMAF |

**11 cas conformes sur 11.**
