# Chantier B — préparation du compte des sociétés (non intégré)

Source : Eurostat `nasa_10_nf_tr` (comptes non financiers par secteur, France, M€ courants, 1995-2025),
fichier `data/raw/eurostat_nasa_10_nf_tr_secteurs_FR.json` ; secteurs S11 (sociétés non financières), S12 (sociétés
financières), S13, S14_S15, S2. Toutes les opérations nécessaires sont disponibles. Script : `b1_cartographie.py`.

## 1. Flux et état dans le modèle (M8)

| Flux | Comptes nationaux | Dans M8 v0.9 |
|---|---|---|
| VA, rémunérations, impôts et subventions sur la production | B1G, D1, D29, D39 | VA et coût du travail par branche marchande ; D29 et D39 au niveau des APU |
| EBE | B2G (S11 : B2A3G) | approché par VA − coût du travail des branches marchandes (inclut les entrepreneurs individuels, champ plus large que S11) |
| Intérêts | D41 (versés, reçus) | absents pour les sociétés (présents pour les APU) |
| Dividendes | D421 | absents, sauf profits induits par une mesure (M14) |
| Bénéfices réinvestis d'IDE | D43 | absents |
| IS | D51 | proportionnel à l'EBE marchand (0,15 × D5 des APU), transfert de bénéfices |
| Épargne, autofinancement | B8G | absents |
| FBCF | P51G | par branche (accélérateur, coût d'usage) ; pas de contrainte de financement |
| Revenus du capital des ménages | D4 reçus par S14 | indexés sur le PIB nominal |

## 2. Ordres de grandeur (S11)

Taux de marge 30-33 % ; dividendes versés nets ≈ 10-16 % de l'EBE ; IS ≈ 12-16 % de l'EBE ; intérêts nets ≈ 2-12 % de
l'EBE (en baisse jusqu'en 2022, remontée en 2024) ; taux d'autofinancement 87-102 %. Identité de l'EBE vérifiée
exactement (B1G − D1 − D29 + D39 = B2A3G).

## 3. Conventions à respecter

- Le CICE est en D39 (2013-2018) : il augmente l'EBE sans réduire D1 ; les allègements (2019 et après) réduisent D1.
- Les intérêts de S12 contiennent les SIFIM : utiliser les intérêts « après SIFIM » publiés (D41) et ne pas modéliser
  S12 par comportement à ce stade (secteur intermédiaire : marge d'intérêt, dividendes reçus et reversés).
- Les dividendes versés par S11 vont aux ménages, à S12, aux APU et au reste du monde ; les dividendes reçus par S11
  (filiales) s'annulent en grande partie en consolidé : modéliser les flux nets.
- Les revenus du capital des ménages doivent devenir la somme des dividendes et intérêts reçus des sociétés et des APU
  (et non une indexation sur le PIB), sous peine de double compte avec les profits induits par M14.

## 4. Architecture proposée (à intégrer après stabilisation du bloc prix)

- Identités : EBE_S11 = VA − D1 − D29 + D39 (champ S11, part de l'EBE marchand de base) ; revenu disponible des sociétés
  = EBE − intérêts nets − dividendes nets − IS − D43 ; B8G ; B9 = B8G − FBCF − variation de stocks (+ transferts en
  capital) ; la dette des sociétés s'accumule par −B9.
- Comportements à estimer (annuel, 1995-2019, tests hors échantillon) :
  - dividendes : correction d'erreur vers une part du résultat courant après intérêts et IS (taux de distribution
    cible), ajustement partiel (type Lintner) ; tester l'effet de la fiscalité des dividendes (2013, PFU 2018) ;
  - intérêts : taux apparent de la dette des sociétés suivant le taux des crédits nouveaux (Banque de France) avec
    renouvellement partiel ;
  - investissement : équation existante + test d'un effet de la profitabilité ou de l'autofinancement (non retenu en
    v0.9) ; ne pas supposer que les profits supplémentaires sont réinvestis.
- Variables exogènes : D43, transferts en capital, part des non-résidents dans les dividendes (M14).
- Fermeture : la capacité de financement des sociétés est un solde ; sa contrepartie (dette, fonds propres) n'affecte
  pas les comportements tant qu'aucun canal financier n'est estimé.
