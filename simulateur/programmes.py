"""Jeux de mesures issus des propositions publiques des candidats à l'élection présidentielle de 2027 (version 0.1,
17 novembre 2026).

Règles communes (neutralité, cahier des charges § 17) :
- mêmes règles de traduction pour tous les candidats ;
- seules les mesures identifiables et chiffrées dans des sources de presse ou institutionnelles sont traduites en
  curseurs ; les programmes ne sont pas complétés pour atteindre les totaux annoncés ;
- quand un montant est présenté comme cumulé sur cinq ans, le montant annuel atteint en fin de mandat est pris égal
  au cumul divisé par 3 (montée en charge linéaire) ;
- quand une durée n'est pas précisée pour un montant pluriannuel, il est réparti sur cinq ans ;
- un taux non précisé est fixé par convention et signalé ;
- tout ce qui n'est pas représentable dans le modèle est listé (« non représenté ») ;
- les candidats dont les propositions économiques ne sont pas encore chiffrées dans des sources fiables à cette date
  ne sont pas traduits (liste NON_TRADUITS), sans jugement sur leur programme.
Ces jeux sont des traductions approximatives, à mettre à jour à mesure que les programmes sont publiés ; ils ne
prétendent pas représenter fidèlement les programmes.
"""
from __future__ import annotations

DATE = "17 novembre 2026"
REGLES = [
    "Mêmes règles de traduction pour tous les candidats ; seules les mesures identifiables et chiffrées dans des sources publiques sont traduites.",
    "Les totaux d'économies annoncés ne sont pas complétés par des économies non détaillées : l'écart entre le total annoncé et les mesures traduites est indiqué.",
    "Montant cumulé sur cinq ans : montant annuel de fin de mandat = cumul ÷ 3 (montée en charge linéaire). Montant pluriannuel sans durée : réparti sur cinq ans.",
    "Taux non précisé : convention signalée. Mesures non représentables dans le modèle : listées.",
    "Ce sont des traductions approximatives, susceptibles d'évoluer avec la publication des programmes ; aucune note n'est attribuée.",
]

PROGRAMMES = [
    {
        "id": "rn", "candidat": "Marine Le Pen", "tri": "Le Pen", "parti": "Rassemblement national",
        "sources": [
            ("Public Sénat, « 140 milliards d'euros d'économies d'ici 2032 », 6 octobre 2026",
             "https://www.publicsenat.fr/actualites/politique/140-milliards-deuros-deconomies-dici-2032-leffort-radical-propose-par-marine-le-pen-pour-redresser-les-f"),
            ("DetteDeLaFrance.fr, contre-budget 2026 du groupe RN (dix mesures chiffrées), analyse du 9 octobre 2026",
             "https://dettedelafrance.fr/presidentielle-2027/rassemblement-national"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"age_legal_immediat": 62, "tva": -1.3, "impots_production": -16, "isf": 0.65, "transferts_menages": -0.1,
                     "autres_depenses": -29, "recettes_neutres": 15},
        "correspondance": [
            "Retour à 62 ans avec 42 annuités (carrières longues : 60 ans) → âge légal 62 ans, retour immédiat (la durée d'assurance n'est pas modélisée).",
            "TVA sur l'énergie ramenée à 5,5 % (11,0 Md€) → taux normal −1,3 point (même rendement ; la répartition par ménage diffère).",
            "Suppression de la CVAE, de la CFE et de la C3S (16,2 Md€) → impôts de production −16 Md€.",
            "Impôt sur la fortune financière remplaçant l'IFI (4,0 Md€ annoncés) → impôt sur la fortune, taux moyen 0,65 %.",
            "Quotient familial : part entière dès le 2e enfant (−2,9 Md€) et conditionnement de prestations pour les étrangers (+6,1 Md€) → transferts nets aux ménages −0,1 point de PIB.",
            "Réorganisation de l'État (20,7 Md€), agences (3,4 Md€), dotations des collectivités (5 Md€) → autres dépenses de fonctionnement −29 Md€.",
            "Contribution à l'UE (−8,7 Md€), fraude (+3,5 Md€), taxe sur les transactions intrajournalières (+3 Md€) → recettes ou économies sans effet sur la demande +15 Md€.",
        ],
        "non_represente": ["Règle d'or constitutionnelle", "Pilier de capitalisation pour les retraites",
                           "Économies liées à l'immigration au-delà des prestations (15 à 29 Md€ annoncés)",
                           "Centralisation des recettes de TVA", "Préférence nationale (effets économiques)"],
        "total_annonce": "140 Md€ d'économies nettes d'ici 2032 et 30 Md€ de baisses d'impôts ; déficit à 3 % en 2030.",
    },
    {
        "id": "lfi", "candidat": "Jean-Luc Mélenchon", "tri": "Mélenchon", "parti": "La France insoumise",
        "sources": [
            ("LCP, « Ce qui change dans le nouveau programme de Jean-Luc Mélenchon », 6 novembre 2026",
             "https://lcp.fr/actualites/presidentielle-2027-ce-qui-change-dans-le-nouveau-programme-de-jean-luc-melenchon-444841"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"smic": 13, "point_indice": 10, "aides_logement": 10, "age_legal": 60, "isf": 1.0, "ir_t4": 60, "pfu": 15,
                     "successions": 20, "minimum_vieillesse": 29},
        "correspondance": [
            "SMIC à 1 700 € net (contre 1 502 € annoncés pour 2027) → coup de pouce de 13 %.",
            "Point d'indice +10 % et APL +10 % → curseurs correspondants.",
            "Abrogation de la réforme de 2023, puis retraite à 60 ans à taux plein « à terme » → âge légal cible 60 ans, transition de 3 mois par génération (les 40 annuités ne sont pas modélisées).",
            "Rétablissement de l'ISF avec volet climatique (taux non précisé) → convention : taux moyen 1 %.",
            "Impôt sur le revenu à 14 tranches (taux non précisés) → convention : taux de la tranche supérieure 60 %.",
            "Suppression de la flat tax → +15 points sur la part impôt sur le revenu (imposition au barème approchée).",
            "Plafonnement de l'héritage à 12 M€ → droits de succession +20 % (convention).",
            "Garantie d'autonomie au seuil de pauvreté (1 337 €) → minimum vieillesse +29 %.",
        ],
        "non_represente": ["Blocage des prix des produits de première nécessité", "Sécurité sociale intégrale",
                           "Cotisation sociale sur les revenus du capital", "Taxe Zucman", "Écart de salaires plafonné de 1 à 20",
                           "Planification écologique (montants non publiés dans les sources consultées)", "Gel de la dette détenue par la BCE"],
        "total_annonce": "Pas de chiffrage global dans les sources consultées.",
    },
    {
        "id": "ps_pp", "candidat": "Raphaël Glucksmann", "tri": "Glucksmann", "parti": "Place publique – Parti socialiste",
        "sources": [
            ("Public Sénat, « Raphaël Glucksmann met 200 milliards sur la table », 9 novembre 2026",
             "https://www.publicsenat.fr/actualites/politique/presidentielle-2027-raphael-glucksmann-met-200-milliards-sur-la-table-et-invite-le-senat-a-voter-en-faveur-dune-future-republique-ecologique"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"investissement_public": 40, "recettes_neutres": 10, "transferts_menages": 0.25, "age_legal": 62},
        "correspondance": [
            "200 Md€ d'investissements publics (durée non précisée) → 40 Md€ par an sur cinq ans (convention).",
            "Contribution exceptionnelle de 5 % sur les patrimoines de plus de 100 M€, une seule année (50 Md€) → 10 Md€ par an lissés sur cinq ans, sans effet sur la demande (approximation : le prélèvement est ponctuel).",
            "Chèque énergie (500 € pour 6 millions de familles, 200 € pour 10 millions), leasing social, pompes à chaleur, pass mobilité → transferts aux ménages +0,25 point de PIB (environ 7,5 Md€).",
            "Abrogation de la réforme de 2023 (âge non précisé) → âge légal cible 62 ans, transition de 3 mois par génération (convention).",
        ],
        "non_represente": ["Baisse de CSG sur les bas salaires (taux non précisé)", "Taxe européenne sur les superprofits pétroliers et gaziers",
                           "Fiscalité aérienne et sur la consommation ostentatoire", "Livret de souveraineté écologique et sociale",
                           "Grand emprunt écologique européen"],
        "total_annonce": "Pas de chiffrage global au-delà des 200 Md€ d'investissements dans les sources consultées.",
    },
    {
        "id": "renaissance", "candidat": "Gabriel Attal", "tri": "Attal", "parti": "Renaissance",
        "sources": [
            ("Public Sénat, « Réduction du nombre de fonctionnaires : le virage à 180 degrés de Gabriel Attal », juillet 2026",
             "https://www.publicsenat.fr/actualites/politique/reduction-de-nombre-de-fonctionnaires-le-virage-a-180-degres-de-gabriel-attal"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"emploi_public": -100, "rsa": -2, "prime_activite": -2, "allocations_familiales": -2, "aides_logement": -2,
                     "indexation_pensions": -0.25},
        "correspondance": [
            "Suppression de 100 000 postes de fonctionnaires d'État (7 Md€) → emplois publics −100 000, atteints en cinq ans.",
            "Gel des prestations sociales la première année → RSA, prime d'activité, allocations familiales et aides au logement −2 % (inflation d'une année).",
            "Gel des pensions hors petites retraites la première année → indexation −0,25 point par an sur cinq ans (≈ −1,25 % cumulé).",
            "Pas de hausse d'impôts ; pas de modification de l'âge légal.",
        ],
        "non_represente": ["Système universel par points avec décote et surcote (paramètres non publiés)", "Pilier de capitalisation",
                           "Réformes des arrêts maladie et de l'assurance chômage (non chiffrées)"],
        "total_annonce": "Effort de 120 à 150 Md€ sur dix ans, deux tiers sur les dépenses sociales ; déficit sous 3 % avant 2032, équilibre en 2037. Les mesures traduites n'en représentent qu'une partie.",
    },
    {
        "id": "horizons", "candidat": "Édouard Philippe", "tri": "Philippe", "parti": "Horizons",
        "sources": [
            ("Euronews, « Édouard Philippe mise sur le travail et la réduction des dépenses publiques », 9 octobre 2026",
             "https://fr.euronews.com/2026/10/09/presidentielle-2027-edouard-philippe-mise-sur-le-travail-et-la-reduction-des-depenses-publ"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"age_legal": 65, "emploi_public": -250, "assurance_chomage": -15, "investissement_public": 2},
        "correspondance": [
            "Âge légal porté à 65 ans en moins de dix ans → âge légal cible 65 ans, 3 mois par génération (les 45 années de cotisation ne sont pas modélisées).",
            "Non-remplacement d'un départ à la retraite sur trois (environ 250 000 postes en cinq ans) → emplois publics −250 000, atteints en cinq ans.",
            "Durée maximale d'indemnisation de 18 à 12 mois avant 50 ans → allocations chômage −15 % (estimation).",
            "Fonds d'adaptation au changement climatique de 2 Md€ par an → investissement public +2 Md€.",
        ],
        "non_represente": ["Allocation familiale unique de 350 € par mois dès le premier enfant (coût non publié)",
                           "Réduction d'impôt d'environ 3 000 € pour les familles qui travaillent (coût non publié)",
                           "Exonération de cotisations pour deux heures supplémentaires par semaine", "Pilier de capitalisation obligatoire",
                           "Durée de cotisation portée à 45 ans"],
        "total_annonce": "Environ 30 Md€ par an d'économies sur les retraites à terme ; moitié de l'effort sur les dépenses sociales.",
    },
    {
        "id": "lr", "candidat": "Bruno Retailleau", "tri": "Retailleau", "parti": "Les Républicains",
        "sources": [
            ("Public Sénat, « Bruno Retailleau s'engage sur un plan d'économies de près de 200 milliards d'euros »",
             "https://www.publicsenat.fr/actualites/economie/presidentielle-2027-bruno-retailleau-sengage-sur-un-plan-deconomies-de-pres-de-200-milliards-deuros-sil-est-elu"),
            ("Public Sénat, propositions des candidats sur les retraites",
             "https://www.publicsenat.fr/actualites/politique/reculer-ou-avancer-lage-legal-avec-ou-sans-capitalisation-ce-que-proposent-les-principaux-candidats-a-lelection-presidentielle-sur-les-retraites"),
        ],
        "curseurs": {"emploi_public": -400, "autres_depenses": -25, "recettes_neutres": 2, "assurance_chomage": -25, "sante": -1,
                     "impots_production": -10, "transferts_menages": 0.25},
        "correspondance": [
            "Non-remplacement de 400 000 départs à la retraite d'agents publics → emplois publics −400 000, atteints en cinq ans.",
            "Autres économies de l'État (opérateurs, base zéro, délégations, formation professionnelle, politiques ciblées, immigration, associations : 66 Md€ cumulés) et des collectivités (10 Md€ cumulés) → autres dépenses −25 Md€ par an en 2032 (cumul ÷ 3).",
            "Lutte contre la fraude (5 Md€ cumulés) → recettes sans effet sur la demande +2 Md€ par an.",
            "Assurance chômage et prestations (30 Md€ cumulés) → allocations chômage −25 % (10 Md€ par an).",
            "Arrêts maladie (4 Md€ cumulés) → dépenses de santé −1 Md€ par an.",
            "Baisse des impôts des entreprises (30 Md€, impôts de production, présentés comme cumulés) → impôts de production −10 Md€ par an.",
            "Baisse des prélèvements des ménages (21 Md€, exonération des heures supplémentaires) → transferts aux ménages +0,25 point de PIB (environ 7 Md€ par an).",
        ],
        "non_represente": ["Âge minimal de 63 ans avec taux plein à 65 ans et décote de 7 % par an (42 Md€ cumulés annoncés) : la décote n'est pas modélisée",
                           "Capitalisation de 25 à 30 % des retraites des nouveaux entrants", "15 Md€ d'économies de protection sociale non détaillées"],
        "total_annonce": "197 Md€ d'économies sur cinq ans, dont 56 Md€ redirigés en baisses d'impôts (l'article cite aussi 51 Md€).",
    },
]

NON_TRADUITS = [
    ("Marine Tondelier (Les Écologistes)", "ISF climatique, TVA verte, fiscalité des transports, retour à 62 ans : taux et montants non publiés dans les sources consultées."),
    ("Fabien Roussel (PCF)", "Hausse du SMIC, retraite à 60 ans, 32 heures : programme 2027 non chiffré dans les sources consultées."),
    ("Éric Zemmour (Reconquête)", "Programme 2027 non chiffré dans les sources consultées (le chiffrage disponible date de 2022)."),
    ("Autres candidats déclarés", "Propositions économiques non chiffrées dans les sources consultées à cette date."),
]
