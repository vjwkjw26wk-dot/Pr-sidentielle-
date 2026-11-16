# Module M1 — Démographie par cohortes (version 2)

**Statut : construit et validé (16 novembre 2026).** Remplace la version 1 (émulateur calé sur Eurostat, écarts de 2 à 4 % en 2070), dont le code n'avait pas été conservé. La version 2 applique la méthode et les hypothèses des projections de population 2026 de l'Insee, publiées par âge et par sexe.

## Variables d'état
`P[s,a,t]` : population au 1er janvier de l'année t, par sexe s et âge révolu a, de 0 à 120 ans (242 effectifs). Les effectifs publiés « 105 ans ou plus » sont répartis sur 105-120 ans au départ selon une survie stationnaire.

## Équations (Lexis : quotients, fécondité et migrations par âge atteint dans l'année A, génération t − A)
```
(1) P[s,A,t+1] = P[s,A−1,t]·(1 − q[s,A,t]) + SM[s,A,t]·(1 − q[s,A,t]/2) + AJ[s,A,t]        A = 1..120
(2) N[t]       = Σ_{A=15..50} f[A,t] · (PF[A−1,t] + PF[A,t+1]) / 2
(3) P[s,0,t+1] = N[t]·π_s·(1 − q[s,0,t]) + SM[s,0,t]·(1 − q[s,0,t]/2) + AJ[s,0,t]          π_F = 100/205
(4) D[s,A,t]   = P[s,A−1,t]·q[s,A,t] + SM[s,A,t]·q[s,A,t]/2
(5) Actifs[t]  = Σ_s Σ_a P[s,a,t] · τ[s,a]
Identité : Ptot[t+1] − Ptot[t] = N[t] − Dtot[t] + SMtot[t] + AJtot[t]   (contrôlée à chaque pas, tolérance 0,001 personne)
```
`AJ` est l'ajustement statistique de l'Insee lié à la méthode du recensement ; il est nul à partir de 2028.

## Paramètres et hypothèses

| Élément | Valeur | Origine | Niveau |
|---|---|---|---|
| Population au 1er janvier 2026 | par sexe et âge | Insee, projections 2026 (population estimée) | A |
| Quotients de mortalité 2026-2070 | par sexe et âge, 0-120 ans | Insee, hypothèses des projections 2026 (central : gains au rythme 2005-2025 hors Covid ; EV 89,5 ans F et 86,7 ans H en 2070) | A |
| Taux de fécondité par âge | 15-50 ans ; ICF 1,45 à partir de 2028 ; âge moyen à la maternité 33,0 ans en 2050 | Insee | A |
| Solde migratoire par sexe et âge | +150 000 par an à partir de 2026 | Insee | A (scénario) |
| Part des filles à la naissance | 100/205 | Insee (vérifié sur les naissances projetées) | A |
| τ taux d'activité | 2024, par sexe et tranche de 5 ans, constants | Eurostat `lfsa_argan` | A (constance : scénario) |

Aucun paramètre n'est calé : le module applique les hypothèses publiées.

## Générateur de scénarios (pour les politiques et variantes)
`GenerateurScenarios` construit des hypothèses à partir du central et de trois variantes de l'Insee, qui fournissent les directions de variation :
- **Fécondité** : calendrier par âge du central conservé, niveau ajusté à l'ICF visé (trajectoire annuelle interpolée).
- **Migrations** : SM = SM_central + (S − 150 000) × profil marginal par sexe et âge, le profil marginal étant celui qu'utilise l'Insee (écart haut − central, identique à central − bas, 50 % femmes).
- **Mortalité**, deux paramétrages au choix : (a) espérance de vie visée en 2070 → déplacement des log-quotients le long des directions « haute » ou « basse » de l'Insee ; (b) rythme des gains relatif au central (0 = mortalité figée en 2025, 2 = gains doublés). Option de choc temporaire (facteur multiplicatif sur une année).

## Validation (`tests/validation_M1.py`, rapport `outputs/validation_M1.md`)

**Test A — réplication des 29 scénarios publiés** (27 scénarios et 2 scénarios de travail ; hypothèses de l'Insee en entrée, départ 2023) : population totale à moins de 3,4·10⁻⁵ en relatif sur 2024-2070 ; naissances et décès à moins de 10⁻³ ; population par âge 0-104 ans à moins de 0,08 % dans les scénarios à mortalité centrale. Seule exception : les scénarios à espérance de vie haute ou basse, avec des écarts de 4 à 5 % sur quelques centaines de personnes aux âges 100-104 en 2026-2030, dus à la répartition initiale du groupe 105 ans ou plus.

**Test B — générateur paramétrique** (départ au 1er janvier 2026, paramètres transmis : trajectoire d'ICF, solde total, espérance de vie féminine 2070) : les 23 scénarios situés dans les directions de l'Insee sont reproduits à moins de 5·10⁻⁶ sur la population totale, effet en 2070 à 5·10⁻⁵ près. Le générateur n'apprend que sur 3 variantes. Ce résultat confirme que l'Insee construit ses scénarios combinés par superposition des mêmes directions ; il ne vaut pas validation pour des hypothèses situées hors de ces directions.

**Hors directions Insee** : « mortalité constante » reproduite exactement avec le paramétrage (b) ; « solde migratoire nul à tous les âges » : effet surestimé de 8,8 %, l'Insee annulant le solde à chaque âge alors que le générateur extrapole le profil marginal en dessous de +70 000.

**Chiffres de référence (central, départ 2026)** : 69,08 M en 2026 ; maximum en 2037 (69,77 M) ; 65,89 M en 2070 ; rapport 65 ans ou plus / 20-64 ans : 40 % (2026), 49 % (2040), 62 % (2070). Actifs de 15-74 ans à taux d'activité 2024 constants : 32,2 M (2026-2040), 28,5 M (2070).

## Limites
1. Soldes migratoires inférieurs à +70 000 : profil par âge extrapolé (voir test B).
2. Population active : seul le scénario à taux constants existe ; la réforme des retraites de 2023 n'est pas prise en compte (lot 2).
3. Composition des ménages : non construite (lot 2).
4. Aucun effet des politiques sur la fécondité, la mortalité ou les migrations : ce sont des scénarios exogènes (décision A5).
5. L'espérance de vie calculée par M1 à partir des quotients (décès en milieu d'année) dépasse d'environ 0,5 an celle que publie l'Insee (90,0 ans contre 89,5 ans pour les femmes en 2070, scénario central). Le paramètre « EV visée » du générateur s'exprime dans la convention de M1 ; une table de correspondance avec la convention de l'Insee reste à établir avant l'ouverture au public.
