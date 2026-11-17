# Déploiement d'un service de calcul exact (version 0.4)

**État : recette prête, non déployée.** Mettre le service en ligne suppose de choisir un hébergeur, de payer un
serveur et de choisir un nom de domaine. Ces décisions reviennent au porteur du projet.

## Pourquoi un serveur

Deux types de calcul coexistent :

- **L'interface publiée** : une page autonome qui additionne des simulations précalculées mesure par mesure. Elle
  répond immédiatement mais ignore les interactions entre mesures. Sur quatre scénarios combinés, la validation
  chiffre l'erreur de cette approximation (`resultats/validation_additivite.md`).
- **Le calcul exact** : il fait tourner toute la chaîne de modèles. Il demande :
  - environ 30 s pour charger le modèle (une fois par processus) ;
  - 15 s par scénario sans mesure sur les ménages ;
  - 2 à 5 minutes au premier calcul d'une nouvelle réforme fiscale ou sociale (OpenFisca), puis le résultat est mis
    en cache ;
  - environ 3 Go de mémoire.

  Ces besoins dépassent les fonctions « sans serveur » (limites de durée et de mémoire). Il faut donc une machine
  virtuelle ou un conteneur permanent.

## Recette

```
docker build -t presidentielle -f deploiement/Dockerfile .
docker run -p 8765:8765 -v presidentielle-donnees:/app/data -v presidentielle-cache:/app/outputs presidentielle
```

**Premier lancement.**
1. Le service télécharge les données ouvertes. Chaque fichier est consigné dans `data/raw/_registre.json` avec son
   URL, sa date et son empreinte SHA-256.
2. Il recale le compte de référence, en environ 10 minutes.
3. Il faut ensuite lancer `python -m simulateur.precalcul` puis `python -m simulateur.interface` dans le conteneur,
   environ 1 heure, pour produire la page servie à `/`.

**Points d'accès.**
- `GET /` : l'interface. Le bouton « Calcul exact » s'affiche automatiquement quand le serveur répond.
- `GET /sante` : version et empreintes du code et des données.
- `POST /executer` : page de résultats.
- `POST /api/executer` : résultats en JSON. Le scénario est au format `{"curseurs": [...]}` (copié depuis
  l'interface) ou `{"mesures": [...]}` (catalogue).

**Dimensionnement indicatif.**
- 2 processeurs et 6 Go de mémoire.
- Les calculs sont faits un à la fois (verrou). Pour un usage public, il faudrait une file d'attente (par exemple
  plusieurs processus servis par un répartiteur), une limite de requêtes par visiteur et un cache des scénarios déjà
  calculés, indexé par l'empreinte du scénario et la version du modèle.

## Reproductibilité

Chaque résultat contient un champ `version` :
- la version du modèle ;
- une empreinte globale du code et une empreinte par module ;
- l'empreinte du registre des données.

L'interface affiche ces empreintes en pied de page. Un résultat se reproduit avec le même code (même commit du dépôt)
et les mêmes fichiers de données (vérifiés par le registre).
