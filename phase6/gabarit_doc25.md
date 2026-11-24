# 25 — Corpus des programmes présidentiels 2027 et correspondance avec le modèle

État au 2026-11-24. Code : `src/m27_corpus.py` (données structurées, sources, règles de conversion),
`src/m26_europe_institutions.py` (qualification européenne). Ce document décrit le corpus ; il ne contient aucune
évaluation ni appréciation des programmes.

## 1. Périmètre et choix des candidats

| Candidat | Document de référence | Chiffrage publié |
|---|---|---|
| Jean-Luc Mélenchon (LFI) | *L'Avenir en commun*, 5ᵉ édition (6 novembre 2026, 1 069 mesures dont 238 nouvelles) ; document budgétaire « Comment nous allons remettre de l'ordre dans les comptes publics » (14 octobre 2026) | année 2027 seulement : 106,4 Md€ de recettes, 81,7 Md€ de dépenses, 25 Md€ de réduction du déficit ; chiffrage complet promis début 2027 |
| Marine Le Pen (RN) | contre-budget et trajectoire (6 octobre 2026) ; réforme des retraites (17 novembre 2026) ; programme en ligne | enveloppe de 140 Md€ d'économies nettes d'ici 2032 ; postes partiellement chiffrés ; retraites 18,6 Md€ bruts en 2032 |
| Édouard Philippe (Horizons) | programme en ligne (15 thèmes, depuis le 12 novembre 2026) ; « volume 1 » (18 novembre 2026) | près de 150 Md€ d'économies et déficit < 2,5 % du PIB en fin de quinquennat ; mesures rarement chiffrées une à une ; « volume 2 » annoncé en janvier 2027 |

Candidat du centre : Édouard Philippe, parce que son programme est publié sous forme structurée et comporte un volet
de finances publiques ; pour Gabriel Attal, les sources consultées ne donnent qu'une enveloppe d'économies (120 à
150 Md€ selon les sources). Le corpus est extensible à d'autres candidats sans changement de code.

## 2. Règles de constitution

1. **Montant** : celui annoncé par le candidat (« candidat ») ; à défaut, chiffrage d'un tiers explicitement cité
   (« tiers ») ; sinon aucun montant (« aucun »). Signe : du point de vue du solde public (+ recette ou économie).
2. **Canal** : curseur(s) du simulateur. Quand le curseur n'est pas exprimé en Md€, sa valeur est obtenue en inversant
   le rendement statique du simulateur à partir du montant annoncé (PFU : 0,6 Md€ par point ; ISF : assiette 930 Md€
   moins l'IFI remplacé ; successions : 18 Md€ ; TVA : 8,2 Md€ par point de taux normal ; assurance chômage : 40 Md€ ;
   IS : rendement de référence de l'IS du modèle par point ; transferts : PIB nominal de 2027 de la référence). On
   simule ainsi la mesure *telle que chiffrée par le candidat* ; le modèle applique ensuite ses propres comportements
   (érosion d'assiette M13, bouclage macroéconomique), ce qui permet de comparer rendement annoncé et rendement simulé.
3. **Hypothèses de correspondance [H]** : toute convention qui ne découle pas du texte est écrite dans la règle de la
   mesure (section 4) et peut être remplacée par une variante.
4. **Quantifiable** : *oui* (montant et canal), *partiel* (canal identifié, montant ou périmètre manquant, ou canal
   approché), *non* (mesure institutionnelle, réglementaire ou sans canal dans le modèle).
5. **Calendrier** : première année d'application par mesure (`Mesure.debut`) ; la traduction (M25) accepte désormais
   des listes de mesures avec dates propres.
6. **Éléments de régime** : règles d'or et objectifs de solde ne sont pas des mesures mais des régimes budgétaires
   (M23) ; ils sont repérés (`Mesure.regime`).

## 3. Tables du corpus
{TABLES}

## 4. Règles de conversion et hypothèses par mesure

{REGLES}

## 5. Bilan de couverture

{COUVERTURE}

Lecture : le paquet 2027 de LFI est entièrement chiffré par le candidat (recettes et dépenses se recoupent exactement
avec les totaux de 106,4 et 81,7 Md€) ; les programmes RN et Horizons sont décrits par des enveloppes agrégées dont
la composition n'est que partiellement publiée. Pour ces deux candidats, une part importante de l'effort annoncé
(économies non ventilées) ne peut entrer dans le modèle que comme hypothèse de composition, ou comme objectif de solde
atteint par la règle budgétaire de M23 (variante « programme = régime »). Les deux lectures devront être présentées
côte à côte dans le rapport.

Mesures non quantifiables dans le modèle (principales) : contrôle des capitaux, fin de la cotation continue,
centralisation de l'épargne réglementée et pôle public bancaire (LFI) ; préférence nationale (RN) ; jours de carence,
nucléaire, ZAN, réorganisation des agences (Horizons) ; piliers de capitalisation (RN, Horizons) ; paramètres fins des
réformes de retraite (durée d'assurance, carrières longues). Voir la liste priorisée des mécanismes manquants (doc 26).

## 6. Points de vigilance relevés pendant la constitution

- **L21** : 8 Md€ pour « 10 % sur les pensions, allocations familiales et APL » n'est pas compatible avec une
  revalorisation générale des pensions ; le périmètre devra être confirmé par le chiffrage complet annoncé.
- **P05-P07** : la décomposition des économies de « réorganisation de l'État » (20,7 Md€) n'indique pas si les
  contributions des collectivités (8,2 Md€) et des agences (3,4 Md€) sont incluses ; traitées comme composantes.
- **P10** : aucun coût n'est publié par le candidat ; ordre de grandeur de l'Institut Montaigne (2022), à actualiser.
- **H11** : l'échange impôts de production contre aides aux entreprises est neutre en montant mais pas en effets selon
  la nature des aides supprimées (subventions, dépenses fiscales, allègements) ; deux variantes.
- **Dates** : les sources de presse se contredisent parfois sur les dates (ex. publication de *L'Avenir en commun*) ;
  on retient les documents des candidats.

## 7. Sources

{SOURCES}

Sources complémentaires de vérification : pages programmes de votons-2027.fr (agrégateur citant les sources
officielles), LCP, Public Sénat, Euronews (dates et montants).
