# Validation des équations de comportement (lot 7)

Généré par `tests/validation_M7.py`. Simulations dynamiques : chaque équation recalcule sa variable année après année à partir de ses propres valeurs simulées ; les autres variables sont observées (équation par équation, sans bouclage). Erreur absolue moyenne (EAM) sur les croissances annuelles, en points ; erreur sur le niveau en fin de période, en %. La prévision naïve prolonge la croissance moyenne de la période d'estimation.

## 1. Coefficients estimés (1997-2019)

### Demande de travail (emploi en personnes), 25 branches

Variable expliquée : Δln emploi ; 575 observations ; R² = 0.67 ; écart type résiduel = 1.5 %.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -0.502 | 0.074 | -6.8 |
| dlq | 0.259 | 0.043 | 6.0 |
| dlq_1 | 0.012 | 0.018 | 0.6 |
| dlh_1 | 0.317 | 0.057 | 5.6 |
| ecm_1 | -0.206 | 0.031 | -6.6 |
| rupture_2008 | 0.003 | 0.001 | 5.3 |

Grandeurs dérivées : élasticité de court terme aux volumes = 0.259 ; vitesse d'ajustement λ = -0.206 ; élasticité de long terme aux volumes (contrainte) = 1.000 ; élasticité de long terme au coût réel (calibrée) = -0.400 ; version libre : élasticité de long terme aux volumes = 0.438 ; version libre : élasticité au coût réel = -0.210.

### Prix de la valeur ajoutée, 25 branches

Variable expliquée : Δln prix VA ; 575 observations ; R² = 0.40 ; écart type résiduel = 3.0 %.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -0.007 | 0.015 | -0.5 |
| dlclu | 0.677 | 0.115 | 5.9 |
| dlq | 0.124 | 0.071 | 1.8 |
| ecm_1 | -0.115 | 0.056 | -2.0 |

Grandeurs dérivées : transmission de court terme du coût salarial unitaire = 0.677 ; effet de court terme de la demande (volume) = 0.124 ; vitesse de retour de la marge λ = -0.115 ; version libre : transmission de long terme (1 = homogénéité) = 0.745.

### Investissement (FBCF en volume), 25 branches : accélérateur

Variable expliquée : Δln FBCF ; 575 observations ; R² = 0.30 ; écart type résiduel = 5.8 %.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -0.734 | 0.508 | -1.4 |
| dlq | 0.670 | 0.204 | 3.3 |
| dlq_1 | 0.256 | 0.097 | 2.6 |
| li_1 | -0.285 | 0.109 | -2.6 |
| lk_1 | 0.191 | 0.096 | 2.0 |
| lq_1 | 0.113 | 0.048 | 2.3 |

Grandeurs dérivées : élasticité de court terme aux volumes = 0.670 ; vitesse λ = -0.285 ; long terme : élasticité aux volumes = 0.395 ; long terme : élasticité au capital installé = 0.671.

### Investissement des sociétés non financières (agrégat)

Variable expliquée : Δln FBCF des SNF ; 23 observations ; R² = 0.82 ; écart type résiduel = 2.2 % ; autocorrélation des résidus (Breusch-Godfrey, p) = 0.88.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -1.024 | 0.334 | -3.1 |
| dlq | 1.946 | 0.333 | 5.8 |
| dlq_1 | 0.258 | 0.384 | 0.7 |
| ecm_1 | -0.395 | 0.139 | -2.8 |
| tm_1 | 0.739 | 0.538 | 1.4 |
| lcu_1 | -0.073 | 0.024 | -3.0 |

Grandeurs dérivées : élasticité de court terme à la valeur ajoutée = 1.946 ; vitesse λ = -0.395 ; long terme : élasticité au coût d'usage du capital = -0.184 ; long terme : semi-élasticité au taux de marge (par point de VA) = 0.019 ; long terme : effet d'une baisse de 1 point du taux d'IS (≈ 25 %) = 0.002.

### Salaire moyen par tête, secteur marchand

Variable expliquée : Δln salaire par tête ; 23 observations ; R² = 0.37 ; écart type résiduel = 0.9 % ; autocorrélation des résidus (Breusch-Godfrey, p) = 0.10.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -0.018 | 0.021 | -0.8 |
| dlpc | 0.394 | 0.222 | 1.8 |
| dlprod | 0.032 | 0.120 | 0.3 |
| ecm_1 | -0.093 | 0.057 | -1.6 |

Grandeurs dérivées : indexation de court terme sur les prix à la consommation = 0.394 ; effet de court terme de la productivité = 0.032 ; vitesse de retour de la part des salaires λ = -0.093 ; effet d'un point d'écart de chômage (calibré) = -0.004 ; effet estimé librement (biaisé par la composition de l'emploi) = 0.007.

### Consommation des ménages (volume)

Variable expliquée : Δln consommation ; 23 observations ; R² = 0.69 ; écart type résiduel = 0.7 % ; autocorrélation des résidus (Breusch-Godfrey, p) = 0.07.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -0.052 | 0.042 | -1.2 |
| dlrdb | 0.784 | 0.194 | 4.0 |
| du | -0.005 | 0.002 | -2.2 |
| ecart_1 | -0.307 | 0.223 | -1.4 |

Grandeurs dérivées : propension marginale de court terme (élasticité) = 0.784 ; vitesse λ = -0.307.

### Importations (volume)

Variable expliquée : Δln importations ; 23 observations ; R² = 0.96 ; écart type résiduel = 1.0 % ; autocorrélation des résidus (Breusch-Godfrey, p) = 0.26.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | -3.055 | 1.089 | -2.8 |
| dld | 1.465 | 0.092 | 15.9 |
| dlprel | -0.114 | 0.101 | -1.1 |
| lm_1 | -0.661 | 0.149 | -4.4 |
| ld_1 | 0.906 | 0.226 | 4.0 |
| lprel_1 | -0.108 | 0.073 | -1.5 |
| t | 0.004 | 0.001 | 3.0 |

Grandeurs dérivées : élasticité à la demande, court terme = 1.465 ; élasticité à la demande, long terme = 1.370 ; élasticité-prix, long terme = -0.163 ; tendance annuelle de pénétration = 0.006 ; vitesse λ = -0.661.

### Exportations (volume)

Variable expliquée : Δln exportations ; 23 observations ; R² = 0.85 ; écart type résiduel = 1.9 % ; autocorrélation des résidus (Breusch-Godfrey, p) = 0.11.

| Variable | Coefficient | Écart type | t |
|---|---|---|---|
| const | 0.002 | 0.005 | 0.4 |
| dldm | 0.711 | 0.094 | 7.5 |
| dlprel | -0.595 | 0.171 | -3.5 |

Grandeurs dérivées : élasticité à la demande mondiale = 0.711 ; élasticité-prix = -0.595 ; tendance des parts de marché (% par an) = 0.177 ; forme à correction d'erreur : λ (t) = -0.247 (-1.6).

## 2. Tests rétrospectifs

### A. Estimation 1997-2012, simulation 2013-2019

| Équation | Croissance annuelle observée | Simulée | EAM | EAM naïve | Erreur de niveau en fin de période | Naïve |
|---|---|---|---|---|---|---|
| Emploi (25 branches) | +0.8 % | +1.3 % | 0.5 | 0.6 | +3.7 % | +0.3 % |
| Prix de la valeur ajoutée (25 branches) | +0.6 % | +1.1 % | 1.1 | 0.5 | +3.3 % | +2.2 % |
| FBCF des branches marchandes | +2.8 % | +1.5 % | 1.5 | 1.2 | -8.7 % | -0.6 % |
| FBCF des sociétés non financières | +2.4 % | +1.5 % | 2.3 | 1.1 | -5.8 % | -0.8 % |
| Salaire moyen par tête | +1.3 % | +1.7 % | 0.7 | 1.1 | +3.3 % | +7.9 % |
| Consommation des ménages | +1.2 % | +1.4 % | 0.7 | 0.8 | +1.4 % | +6.0 % |
| Importations | +3.7 % | +4.0 % | 1.0 | 1.2 | +2.1 % | +6.7 % |
| Exportations | +3.1 % | +3.1 % | 0.8 | 1.1 | -0.4 % | +6.7 % |

### B. Estimation 1997-2019, simulation 2022-2024

| Équation | Croissance annuelle observée | Simulée | EAM | EAM naïve | Erreur de niveau en fin de période | Naïve |
|---|---|---|---|---|---|---|
| Emploi (25 branches) | +1.6 % | +2.6 % | 1.0 | 1.0 | +3.0 % | -2.2 % |
| Prix de la valeur ajoutée (25 branches) | +2.8 % | +2.1 % | 1.4 | 2.2 | -2.1 % | -5.7 % |
| FBCF des branches marchandes | +1.9 % | +1.9 % | 1.4 | 2.1 | +0.1 % | +2.6 % |
| FBCF des sociétés non financières | +2.1 % | +5.5 % | 6.9 | 1.8 | +10.7 % | +0.5 % |
| Salaire moyen par tête | +4.1 % | +3.3 % | 0.8 | 2.1 | -2.4 % | -6.1 % |
| Consommation des ménages | +1.9 % | +2.8 % | 1.5 | 1.3 | +3.0 % | -0.4 % |
| Importations | +2.6 % | +4.9 % | 2.3 | 4.6 | +7.0 % | +5.2 % |
| Exportations | +4.7 % | +2.7 % | 2.0 | 2.3 | -5.9 % | -2.9 % |

