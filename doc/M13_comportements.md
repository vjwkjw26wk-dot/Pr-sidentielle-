# M13 — Réactions des hauts revenus et des patrimoines (version 0.1, novembre 2026)

**État : opérationnel, paramètres issus de la littérature. Niveau de preuve C à D.**
Code : `src/m13_comportements.py`. Le module est appliqué dans `simulateur/executer.py`.

**Objet.** Le module corrige le rendement statique des mesures qui visent les hauts revenus et les patrimoines. Les
réactions prises en compte sont l'optimisation, la moindre déclaration, la moindre accumulation et les départs (« fuite
des riches et des cerveaux »). Le module traduit une demande de l'utilisateur du 17 novembre 2026. Chaque effet est
donné en fourchette basse, centrale et haute. Seule la valeur centrale entre dans le modèle macroéconomique ; la
fourchette est restituée dans l'interface.

| Mesure | Mécanisme | Paramètre central (fourchette) | Sources |
|---|---|---|---|
| Taux des tranches supérieures de l'impôt sur le revenu (3e et 4e tranches) | Élasticité du revenu imposable e ; perte = e · a · τ/(1−τ) du rendement statique, avec a = 2 (Pareto) et τ le taux marginal total | e = 0,2 (0,1-0,4) | Saez (2001) ; Cabannes, Houdré et Landais (2014) ; Lehmann, Marical et Rioux (2013) ; Garbinti, Goupille-Lebret et Piketty (2018) |
| Prélèvement forfaitaire unique | Élasticité des revenus distribués | 0,5 (0,2-1,0) | Bach, Bozio, Guillouzouic et Malgouyres (2023), réforme de 2018 |
| Impôt sur la fortune | Érosion de l'assiette déclarée et départs ; part perdue croissante sur 5 ans | 25 % puis 35 % (10-50 %) | Jakobsen et al. (2020) ; Seim (2017) ; Brülhart et al. (2022) ; DGFiP (départs avant 2017) |
| Droits de succession | Anticipation (donations, assurance vie) | 10 % (0-25 %) | ordre de grandeur, hypothèse D |
| Mobilité des hauts revenus et des diplômés | Élasticité de la localisation au taux net de prélèvement ; nombre de départs donné à titre indicatif | 0,15 (0,1-0,25) | Kleven, Landais et Saez (2013) ; Kleven et al. (2014) |

**Limites.**
- Les élasticités sont estimées sur des réformes de taille modérée. Leur transposition à des taux très élevés est une
  hypothèse.
- L'effet des départs sur la croissance (entrepreneuriat, innovation) n'est pas modélisé : aucune estimation robuste
  n'est disponible.
- La mobilité des diplômés n'agit pas sur la population active : les effectifs concernés sont trop faibles pour être
  visibles à l'échelle macroéconomique.
- L'assiette de l'impôt sur la fortune est reconstituée à partir de l'ISF 2017, revalorisé, soit environ 930 Md€
  taxables au-delà du seuil. Le produit de l'IFI (2,2 Md€) est déduit, car l'ISF le remplace.
