# 17 — Modèle v0.7 : équations ajoutées ou modifiées

Ce document décrit, équation par équation, les changements de la v0.7 par rapport à la v0.6. Les paramètres, leurs
fourchettes et leurs sources sont dans le document 16. Le code est dans `src/m8_modele.py` (bloc macroéconomique),
`src/m8_reference.py` (référence), `src/m15_offre_travail.py` (offre de travail), `src/m10_couplage.py` (groupes de
ménages) et `simulateur/executer.py` (traduction des mesures). La v0.6 est conservée telle quelle dans `modele_v06/`
et dans l'historique Git.

## 1. Bloc d'offre et fermeture

**PIB potentiel** (Cobb-Douglas, rendements constants) :

    ln Y*_t = lpgf_t + α ln K_{t−1} + (1 − α) ln N*_t + Σ_{s≤t} π_s,      N*_t = PA_t (1 − u*_t)

K : capital des branches marchandes ; PA : population active ; u* : chômage structurel ; π : chocs de productivité
(points de log par an) ; α = 0,35. La productivité globale des facteurs `lpgf` est celle qu'implique la référence
calée, pour laquelle l'écart de production vaut −1,5 (u − u*) (loi d'Okun) : la référence est donc inchangée par
construction (vérifié : écart maximal de chômage de 0,04 point entre les deux fermetures sur 2023-2047).

**Écart de production** : g_t = ln Y_t − ln Y*_t.

**Fermeture** (supplément de demande intérieure Z, en part de la demande de l'année de base, réparti 60 % en
consommation, 40 % en investissement) :

    Z_t = Z_{t−1} − ρ g_{t−1} − a (g_{t−1} − g_{t−2}) + θ (ln Y*_{t−1} − ln Y*ref_{t−1})

ρ = 0,15 (terme intégral), a = 0,3 (terme proportionnel), θ = 1,5 (anticipation). Le terme θ représente la révision
du revenu permanent par les ménages et les entreprises quand le potentiel s'écarte de la référence : sans lui, un choc
d'offre progressif (rampe) laisse un écart de production permanent (erreur de traînage d'un correcteur intégral).
Valeurs testées par simulation (`phase3/test_fermeture.py`, résultats dans `phase3/resultats/test_fermeture_*.json`) :

| θ | Écart de production 2037 (choc de productivité) | Dette 2047 | Commentaire |
|---|---|---|---|
| 0 | +1,75 % | +2 pt | écart permanent, prix en hausse |
| 1,0 | +0,67 % | −11 pt | écart réduit |
| 1,5 | +0,14 % | +7,5 pt | retenu |
| 2,0 | −0,43 % | +25 pt | dépassement, hausse du chômage |

Ces essais ont été faits sur une version intermédiaire, avant l'ajout du terme d'approfondissement du capital dans
l'équation d'emploi (section 2) ; avec la version finale et θ = 1,5, le choc de productivité donne un écart de
production de +0,17 % en 2037, une dette supérieure de 1,8 point en 2037 et de 20 points en 2047 à la référence
(`phase3/resultats/test_fermeture_0.3.json`).

Le terme proportionnel a = 0,3 a été retenu après essais (0 : instable ; 0,1 : oscillations ; 0,6 et 1,0 :
instables).

**Ancienne fermeture** (v0.6) disponible par l'hypothèse `fermeture_mode = "chomage"`.

## 2. Prix, importations, salaires

- Prix de la valeur ajoutée hors branches à taux d'utilisation des capacités (industrie) : + κ g_{t−1}, κ = 0,10.
- Importations : + μ (g_{t−1} − g_{t−2}), μ = 0,3. Une valeur de 1,0 provoquait une oscillation de période deux ans
  (diagnostic par réponse indicielle, `phase3/reponse_Z.py`).
- Salaires : la courbe de Phillips est multipliée par 0,5 quand le chômage est au-dessus de u* (rigidité à la baisse).
- Emploi : le choc de productivité cumulé entre dans la cible de long terme de l'équation à correction d'erreur (en
  v0.6, la correction d'erreur effaçait le choc en quelques années ; défaut corrigé).
- Emploi : approfondissement du capital. La cible de long terme de l'emploi baisse de α/(1 − α) × (dk − dq), où dk et
  dq sont les écarts du capital marchand et du PIB à la référence. Sans ce terme, une hausse de la production due au
  seul capital (investissement public, relocalisation) créait des emplois au rythme de la production, et le chômage
  restait durablement sous u* alors que l'écart de production était nul : incohérence entre l'équation d'emploi et
  la fonction de production.

## 3. Ménages

- Consommation : −0,3 % par point de hausse du chômage (épargne de précaution), −0,2 % par point de hausse du taux
  d'intérêt réel.
- Offre de travail (M15) : marges extensive et intensive, cinq configurations familiales, gains à l'emploi et taux
  marginaux calculés par OpenFisca-France ; la population active et les heures sont modifiées par les mesures de RSA,
  prime d'activité, allocations familiales, aides au logement, impôt sur le revenu (1re tranche) et CSG.
- Assurance chômage : u* varie de 0,063 point par 10 % de variation des allocations (élasticité de durée 0,3).
- Stabilisateur automatique : la dépense d'indemnisation (1,5 % du PIB de base) est proportionnelle au nombre de
  chômeurs.

## 4. Entreprises

- Impôt sur les sociétés : base × [1 − 0,5 (1 − exp(−0,8 Δτ/100))] (transfert de bénéfices des groupes).
- Investissement : + 10 % des bénéfices conservés (canal de trésorerie) ; une baisse d'IS n'augmente donc
  l'investissement que par ce canal.
- Industries énergo-intensives (papier, chimie, minéraux non métalliques, métallurgie) : importations
  supplémentaires d'élasticité 0,15 au prix relatif de l'énergie (par rapport à 2025).
- TVA : répercussion asymétrique et étalée (hausse 95 %, baisse 50 % pour le taux normal ; 50 % et 25 % pour les taux
  réduits ; 60 % la première année) ; la part non répercutée accroît les marges.
- R&D (levier exploratoire) : 1 € d'aide → 0,7 € de R&D privée supplémentaire, comptée en investissement ; élasticité
  de la production au stock de R&D 0,08 ; délai 2 ans.
- Formation (levier exploratoire) : −0,02 point de u* par milliard dépensé durablement, sur 5 ans.

## 5. Distribution

La microsimulation (M10) publie désormais, en plus des déciles, la variation de niveau de vie par âge de la personne de
référence, catégorie sociale, région et configuration familiale (`groupes`), avec les parts de gagnants et de perdants.

## 6. Limites qui demeurent

- Les effets distributifs restent statiques (microsimulation de l'année de base) ; les effets macroéconomiques ne sont
  pas redistribués par décile.
- Pas de bilans patrimoniaux ni d'effets de richesse ; pas de politique monétaire propre à la France ; taux
  souverains exogènes (hors module zone euro M11).
- Les leviers « recherche » et « formation » sont exploratoires ; leur effet de long terme est très incertain.
- La convention « autres dépenses publiques proportionnelles au PIB nominal » est conservée.
