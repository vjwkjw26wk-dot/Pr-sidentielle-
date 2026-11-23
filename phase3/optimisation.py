"""Phase 3, mission C — première optimisation multicritère des politiques publiques (modèle v0.7).

Méthode
1. Métamodèle : la réponse du modèle complet à chaque levier, simulée seule (phase3/resultats/experiences_v07_*.json),
   est mise à l'échelle linéairement ; pour les leviers dont l'effet est asymétrique (TVA, IS, cotisations, RSA,
   assurance chômage, durée du travail, âge légal, transferts, investissement public), la hausse et la baisse ont des
   réponses distinctes. L'additivité est vérifiée a posteriori : chaque stratégie retenue est resimulée avec le modèle
   complet (phase3/verifier_strategies.py), et l'écart métamodèle / modèle est publié.
2. Critères (écarts à la référence) : PIB en volume, chômage, dette publique, revenu disponible réel, niveau de vie des
   30 % les plus modestes (microsimulation statique), indice de Gini, productivité, part de l'industrie ; aux horizons
   5, 10, 15 et 20 ans (2032, 2037, 2042, 2047).
3. Front de Pareto : 40 000 portefeuilles tirés au hasard dans les bornes (chaque portefeuille active entre 3 et 12
   leviers) ; part des solutions dominées.
4. Stratégies : chacune maximise un objectif explicite sous contraintes explicites (programme linéaire en nombres
   mixtes), plutôt qu'une somme pondérée arbitraire ; la stratégie « optimisation globale » maximise le minimum des
   critères normalisés (point de Tchebychev), sans pondération.
5. Robustesse aux préférences : 2 000 jeux de poids tirés uniformément sur le simplexe ; fréquence d'emploi de chaque
   levier dans l'optimum correspondant.
"""
import json
import pathlib
import sys

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

R = pathlib.Path(__file__).resolve().parents[1]
import os
RES = pathlib.Path(os.environ.get("RES_OPTIM", R / "phase3" / "resultats"))
DISTRIB_DYN = os.environ.get("DISTRIB_DYN", "0") == "1"
HORIZONS = (2032, 2037, 2042, 2047)

# levier : (expérience hausse, valeur, expérience baisse, valeur, borne basse, borne haute, difficulté, famille)
# difficulté : 1 réglementaire ou budgétaire simple ; 2 loi ordinaire, opposition sectorielle ; 3 réforme structurelle,
# forte opposition ou risque juridique (droit de l'UE, Conseil constitutionnel)
LEVIERS = {
    "ir_t1":                  ("ir_bas", 2.0, None, None, -2, 2, 2, "impôts"),
    "ir_t4":                  ("ir_haut", 10.0, None, None, -5, 10, 2, "impôts"),
    "csg_activite":           ("csg", 1.0, "csg_moins1", -1.0, -1.5, 1.5, 2, "impôts"),
    "tva":                    ("tva", 1.0, "tva_moins1", -1.0, -2, 2.5, 2, "impôts"),
    "tva_reduite":            ("tva_reduite", 2.0, "tva_reduite_moins2", -2.0, -2, 2, 2, "impôts"),
    "isf":                    ("isf", 1.0, None, None, 0, 1.0, 3, "impôts"),
    "pfu":                    ("pfu", 15.0, None, None, -4, 10, 2, "impôts"),
    "taux_is":                ("is_moins_hausse", 2.2, "is_baisse", -5.8, -5.8, 4.7, 2, "impôts"),
    "impots_production":      ("production", 10.0, None, None, -15, 5, 2, "entreprises"),
    "cotisations_employeurs": ("cotisations", 10.0, "cot_moins20", -20.0, -20, 10, 2, "entreprises"),
    "successions":            ("successions", 50.0, None, None, -30, 50, 3, "impôts"),
    "taxe_carbone":           ("carbone", 50.0, None, None, 0, 100, 3, "impôts"),
    "smic":                   ("smic5", 5.0, None, None, 0, 8, 2, "salaires"),
    "point_indice":           ("point3", 3.0, None, None, -2, 5, 1, "dépenses"),
    "emploi_public":          ("emploi_public", -170.0, None, None, -170, 100, 2, "dépenses"),
    "autres_depenses":        ("fonctionnement", -10.0, None, None, -20, 10, 2, "dépenses"),
    "sante":                  ("sante", -10.0, None, None, -10, 10, 3, "dépenses"),
    "education":              ("education", -10.0, None, None, -10, 10, 2, "dépenses"),
    "defense":                ("defense", -10.0, None, None, -5, 15, 2, "dépenses"),
    "investissement_public":  ("invest_public20_bis", 20.0, "invest_public_moins", -10.0, -10, 30, 2, "investissement"),
    "indexation_pensions":    ("indexation", -1.0, None, None, -1, 0.5, 3, "retraites"),
    "assurance_chomage":      ("chomage_moins10", -10.0, None, None, -25, 10, 3, "prestations"),
    "allocations_familiales": ("af25", 25.0, None, None, -10, 25, 2, "prestations"),
    "aides_logement":         ("apl_moins10", -10.0, None, None, -10, 10, 2, "prestations"),
    "rsa":                    ("rsa25", 25.0, "rsa_moins10", -10.0, -10, 25, 2, "prestations"),
    "prime_activite":         ("ppa25", 25.0, None, None, -10, 50, 1, "prestations"),
    "minimum_vieillesse":     ("aspa25", 25.0, None, None, 0, 25, 1, "prestations"),
    "transferts_menages":     ("transferts_plus", 0.3, "transferts_moins", -0.3, -0.3, 0.3, 2, "prestations"),
    "logements_sociaux":      ("logements_sociaux", 50.0, None, None, 0, 100, 2, "investissement"),
    "reindustrialisation":    ("reindus10", 10.0, None, None, 0, 20, 3, "industrie"),
    "droits_douane":          ("douanes10", 10.0, None, None, 0, 10, 3, "industrie"),
    "temps_travail":          ("temps37", 2.0, "temps32", -3.0, -1, 2, 3, "travail"),
    "age_legal":              ("age65", 1.0, "age62", -2.0, -2, 2, 3, "retraites"),
    "recherche":              ("recherche3", 3.0, None, None, 0, 6, 1, "productivité"),
    "formation":              ("formation2", 2.0, None, None, 0, 4, 1, "productivité"),
}
# Niveau de preuve des effets (périmètres d'optimisation)
# A : instruments fiscaux et budgétaires, effets par les équations estimées et la microsimulation ;
# B : réformes structurelles dont l'effet passe par une hypothèse de comportement documentée (littérature) ;
# C : leviers exploratoires ou objectifs dont la réalisation est supposée (relocalisation, R&D, formation, douane), ou
#     dont l'effet de long terme repose sur une hypothèse non estimée (durée du travail : part des heures supplémentaires
#     convertie en production, hypothèse D de la v0.6, extrapolée des 35 heures).
NIVEAU = {"age_legal": "B", "temps_travail": "C", "assurance_chomage": "B", "taux_is": "B", "smic": "B",
          "reindustrialisation": "C", "recherche": "C", "formation": "C", "droits_douane": "C"}
PERIMETRES = {"principal": ("A", "B"), "avec_exploratoires": ("A", "B", "C"), "instruments_budgetaires": ("A",)}
VALEUR_ACTUELLE = {"ir_t1": 11, "ir_t4": 45, "taux_is": 25.8, "temps_travail": 35, "age_legal": 64}

CRITERES = {  # nom : (description, sens : +1 si « plus » est souhaitable)
    "pib": ("PIB en volume (%)", +1),
    "chomage": ("Taux de chômage (points)", -1),
    "dette": ("Dette publique (points de PIB)", -1),
    "rdb_reel": ("Revenu disponible réel des ménages (%)", +1),
    "modestes": ("Niveau de vie des 30 % les plus modestes (%, statique)", +1),
    "gini": ("Indice de Gini (×100, statique)", -1),
    "productivite": ("Productivité apparente du travail (%)", +1),
    "industrie": ("Part de l'industrie dans la valeur ajoutée (points)", +1),
}
if DISTRIB_DYN:   # v0.8 : services publics (moyens, Md€) parmi les critères ; distribution après propagation
    CRITERES["services"] = ("Moyens des services publics (Md€ par an)", +1)


EXTRAS = ["solde", "investissement", "interets", "salaire_reel", "exportations", "emploi", "pauvrete", "mediane"] + ([] if DISTRIB_DYN else ["services"])


def charger():
    exp = {}
    for f in sorted(RES.glob("experiences_v07_*.json")):
        if "comportements" in f.name:
            continue
        exp.update(json.loads(f.read_text()))
    return exp


def reponse(e):
    """Vecteur de réponse d'une expérience : critères × horizons (dict)."""
    tr = e["traj"]
    out = {}
    for t in HORIZONS:
        s = str(t)
        def g(k, typ):
            if k not in tr:
                return 0.0
            sc, rf = tr[k]["scenario"].get(s), tr[k]["reference"].get(s)
            if sc is None or rf is None:
                return 0.0
            return 100 * (sc / rf - 1) if typ == "pct" else sc - rf
        rdb = 100 * ((tr["rdb"]["scenario"][s] / tr["pc"]["scenario"][s]) / (tr["rdb"]["reference"][s] / tr["pc"]["reference"][s]) - 1)
        prod = 100 * ((tr["pib"]["scenario"][s] / tr["emploi"]["scenario"][s]) / (tr["pib"]["reference"][s] / tr["emploi"]["reference"][s]) - 1)
        out[t] = {"pib": g("pib", "pct"), "chomage": g("chomage", "pt"), "dette": g("dette_pib", "pt"), "rdb_reel": rdb,
                  "productivite": prod, "industrie": g("part_industrie", "pt"), "solde": g("solde_pib", "pt"),
                  "investissement": g("fbcf", "pct"), "interets": g("interets_pib", "pt"),
                  "salaire_reel": 100 * ((tr["salaire"]["scenario"][s] / tr["pc"]["scenario"][s]) / (tr["salaire"]["reference"][s] / tr["pc"]["reference"][s]) - 1),
                  "exportations": g("x", "pct"), "emploi": g("emploi", "pt")}
    dist = e.get("distribution") or []
    if dist:
        rev = sum(d["revenu_M€"] for d in dist if d["decile"] <= 3)
        mas = sum(d["masse_M€"] for d in dist if d["decile"] <= 3)
        modestes = 100 * mas / rev
        ineg = e.get("inegalites") or {}
        gini = 100 * (ineg["apres"]["gini"] - ineg["avant"]["gini"]) if ineg else 0.0
        pauvrete = (ineg["apres_seuil_fixe"]["taux_pauvrete"] - ineg["avant"]["taux_pauvrete"]) if ineg else 0.0
        mediane = 100 * (ineg["apres"]["mediane"] / ineg["avant"]["mediane"] - 1) if ineg else 0.0
        deciles = [d["variation_pct"] for d in sorted(dist, key=lambda d: d["decile"])]
    else:
        modestes, gini, deciles, pauvrete, mediane = 0.0, 0.0, [0.0] * 10, 0.0, 0.0
    for t in HORIZONS:
        out[t].update(modestes=modestes, gini=gini, pauvrete=pauvrete, mediane=mediane)
    out["deciles"] = deciles
    # v0.8 (phase 3.1, option DISTRIB_DYN=1) : critères distributifs après propagation macroéconomique (M16), par
    # horizon (2032 → 2030, 2037 → 2035, 2042 → 2040, 2047 → 2047), et pertes par décile après propagation (2035)
    dd = e.get("distribution_dynamique")
    if DISTRIB_DYN and dd:
        corr = {2032: "2030", 2037: "2035", 2042: "2040", 2047: "2047"}
        for t in HORIZONS:
            d = dd[corr[t]]
            g_ = d["global"]
            out[t].update(modestes=float(np.mean([d["decile"][str(i)]["pct"] for i in (1, 2, 3)])),
                          gini=100 * (g_["gini_apres"] - g_["gini_avant"]), pauvrete=g_["pauvrete_apres"] - g_["pauvrete_avant"],
                          mediane=g_["variation_niveau_de_vie_median_pct"], rdb_reel_menages=g_["pct_moyen"])
        out["deciles"] = [dd["2035"]["decile"][str(i)]["pct"] for i in range(1, 11)]
    # services publics (indicateur de moyens, faute de mesure de la qualité) : Md€ de santé, éducation, fonctionnement,
    # emplois publics (50 k€ par emploi) et point d'indice (1 % ≈ 2,2 Md€)
    cur = e.get("curseurs") or {}
    serv = sum(float(cur.get(k, 0.0)) for k in ("sante", "education", "autres_depenses")) + 0.05 * float(cur.get("emploi_public", 0.0)) \
        + 2.2 * float(cur.get("point_indice", 0.0))
    for t in HORIZONS:
        out[t]["services"] = serv
    return out


def metamodele(exp, niveaux=("A", "B", "C")):
    """Variables de décision : pour chaque levier, une variable « hausse » (≥ 0) et, si l'effet est asymétrique, une
    variable « baisse » (≥ 0). Renvoie la liste des variables et la matrice des réponses unitaires."""
    var = []   # (levier, sens, borne, réponse unitaire)
    for lev, (eh, vh, eb, vb, lo, hi, dif, fam) in LEVIERS.items():
        if NIVEAU.get(lev, "A") not in niveaux:
            continue
        if eh not in exp or "erreur" in exp[eh]:
            print("expérience manquante :", lev, eh, file=sys.stderr)
            continue
        rh = reponse(exp[eh])
        if eb and eb in exp and "erreur" not in exp[eb]:
            rb = reponse(exp[eb])
            up = (rh, vh) if vh > 0 else (rb, vb)
            dn = (rb, vb) if vb < 0 else (rh, vh)
        else:
            up = dn = (rh, vh)
        if hi > 0:
            var.append((lev, +1, hi, _unit(*up, +1)))
        if lo < 0:
            var.append((lev, -1, -lo, _unit(*dn, -1)))
    return var


def _unit(r, v, sens):
    """Réponse pour une unité du levier dans le sens indiqué (sens × |unité|)."""
    k = sens / v   # v négatif et sens −1 → k > 0 : l'expérience est dans le bon sens
    out = {t: {c: k * x for c, x in r[t].items()} for t in HORIZONS}
    out["deciles"] = [k * x for x in r["deciles"]]
    return out


def matrice(var, t):
    """Matrice critères (lignes) × variables (colonnes) à l'horizon t."""
    noms = list(CRITERES) + EXTRAS
    A = np.array([[v[3][t][c] for v in var] for c in noms])
    return noms, A


def evaluer(var, x):
    res = {t: {} for t in HORIZONS}
    for t in HORIZONS:
        noms, A = matrice(var, t)
        y = A @ x
        res[t] = dict(zip(noms, map(float, y)))
    res["deciles"] = [float(sum(v[3]["deciles"][d] * xi for v, xi in zip(var, x))) for d in range(10)]
    return res


def leviers_de(var, x, seuil=1e-4):
    out = {}
    for (lev, s, b, _), xi in zip(var, x):
        if xi > seuil * b:
            out[lev] = out.get(lev, 0.0) + s * float(xi)
    return {k: round(v, 3) for k, v in out.items() if abs(v) > 1e-9}


# ---------------------------------------------------------------------------------------------------------------
# Optimisation sous contraintes (programme linéaire en nombres mixtes)
# ---------------------------------------------------------------------------------------------------------------
def resoudre(var, objectif, contraintes, t_obj=2037, max_leviers=8, max_difficulte=None, exclus=()):
    """objectif : dict critère → poids (signe déjà orienté « plus est mieux ») à l'horizon t_obj, ou "tchebychev".
    contraintes : liste de (critère, horizon, "<=" | ">=", valeur) ; critère "decile_min" : perte maximale par décile (%).
    Une variable binaire par sens de chaque levier : un levier n'est utilisé que dans un sens ; au plus `max_leviers`
    leviers actifs ; somme des difficultés bornée par `max_difficulte` (si fourni)."""
    n = len(var)
    tcheb = objectif == "tchebychev"
    N = 2 * n + (1 if tcheb else 0)       # x (n), z (n) [, t]
    c = np.zeros(N)
    rows, lo, hi = [], [], []

    def ligne(crit, t):
        noms, A = matrice(var, t)
        r = np.zeros(N)
        r[:n] = A[noms.index(crit)]
        return r

    if tcheb:
        c[-1] = -1.0
        for crit, (lib, sens) in CRITERES.items():
            r = ligne(crit, t_obj) * sens / NORM[crit]
            r[-1] = -1.0
            rows.append(r); lo.append(0.0); hi.append(np.inf)
    else:
        for crit, w in objectif.items():
            c -= w * ligne(crit, t_obj) / NORM[crit]
    for crit, t, op, val in contraintes:
        if crit == "decile_min":
            for d in range(10):
                r = np.zeros(N)
                r[:n] = [v[3]["deciles"][d] for v in var]
                rows.append(r); lo.append(val); hi.append(np.inf)
            continue
        r = ligne(crit, t)
        rows.append(r); lo.append(val if op == ">=" else -np.inf); hi.append(val if op == "<=" else np.inf)
    for i, v in enumerate(var):               # x_i ≤ borne_i · z_i
        r = np.zeros(N); r[i] = 1.0; r[n + i] = -v[2]
        rows.append(r); lo.append(-np.inf); hi.append(0.0)
    for lev in sorted({v[0] for v in var}):   # un seul sens par levier
        r = np.zeros(N)
        for i, v in enumerate(var):
            if v[0] == lev:
                r[n + i] = 1.0
        rows.append(r); lo.append(-np.inf); hi.append(1.0)
    if max_leviers:
        r = np.zeros(N); r[n:2 * n] = 1.0
        rows.append(r); lo.append(-np.inf); hi.append(max_leviers)
    if max_difficulte:
        r = np.zeros(N); r[n:2 * n] = [LEVIERS[v[0]][6] for v in var]
        rows.append(r); lo.append(-np.inf); hi.append(max_difficulte)
    ub = np.array([(0.0 if (v[0], v[1]) in exclus else v[2]) for v in var] + [1] * n + ([np.inf] if tcheb else []))
    lb = np.array([0.0] * (2 * n) + ([-np.inf] if tcheb else []))
    integ = np.array([0] * n + [1] * n + ([0] if tcheb else []))
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), bounds=Bounds(lb, ub), integrality=integ,
               options={"time_limit": 60})
    if res.x is None:
        return None
    return res.x[:n]


NORM = {}


def echantillon(var, n=40_000, graine=0):
    """Portefeuilles aléatoires (entre 3 et 12 leviers actifs, valeurs uniformes dans les bornes)."""
    rng = np.random.default_rng(graine)
    leviers = sorted({v[0] for v in var})
    idx = {l: [i for i, v in enumerate(var) if v[0] == l] for l in leviers}
    X = np.zeros((n, len(var)))
    for k in range(n):
        act = rng.choice(leviers, size=rng.integers(3, 13), replace=False)
        for l in act:
            i = rng.choice(idx[l])
            X[k, i] = rng.uniform(0, var[i][2])
    return X


def criteres_echantillon(var, X, t):
    noms, A = matrice(var, t)
    Y = X @ A.T
    return {c: Y[:, noms.index(c)] for c in noms}


def pareto(Y):
    """Indices non dominés (tous critères orientés « plus est mieux »)."""
    n = Y.shape[0]
    dom = np.zeros(n, dtype=bool)
    ordre = np.argsort(-Y.sum(axis=1))
    front = []
    for i in ordre:
        if dom[i]:
            continue
        domine = np.all(Y[front] >= Y[i], axis=1) & np.any(Y[front] > Y[i], axis=1) if front else np.array([False])
        if domine.any():
            dom[i] = True
            continue
        front.append(i)
    return np.array(front)


STRATEGIES = {
    "S1_protection": {
        "libelle": "Protection sociale et pouvoir d'achat",
        "objectif": {"modestes": 1.0, "rdb_reel": 1.0},
        # définition de la stratégie : pas de réduction des droits sociaux ni des services publics de santé et d'éducation
        "exclus": [("age_legal", 1), ("indexation_pensions", -1), ("assurance_chomage", -1), ("rsa", -1), ("aides_logement", -1),
                   ("allocations_familiales", -1), ("prime_activite", -1), ("sante", -1), ("education", -1), ("emploi_public", -1)],
        "contraintes": [("dette", 2037, "<=", 0.0), ("dette", 2047, "<=", 0.0), ("chomage", 2037, "<=", 0.0),
                        ("decile_min", None, ">=", -0.5)],
    },
    "S2_emploi": {
        "libelle": "Compétitivité et emploi",
        "objectif": {"chomage": -1.0},
        "contraintes": [("dette", 2037, "<=", 0.0), ("exportations", 2037, ">=", 0.0), ("pib", 2037, ">=", 0.0),
                        ("modestes", 2037, ">=", -0.5), ("decile_min", None, ">=", -1.0)],
    },
    "S3_productivite": {
        "libelle": "Productivité et transformation industrielle",
        # capacité de production à 15 ans, avec une productivité par emploi en hausse et sans destruction d'emplois
        "objectif": {"pib": 1.0},
        "t_obj": 2042,
        "contraintes": [("dette", 2042, "<=", 0.0), ("productivite", 2042, ">=", 0.5), ("emploi", 2042, ">=", 0.0),
                        ("investissement", 2037, ">=", 0.0), ("modestes", 2037, ">=", -0.5), ("decile_min", None, ">=", -1.0)],
    },
    "S4_redressement": {
        "libelle": "Redressement budgétaire accéléré",
        "objectif": {"dette": -1.0},
        "contraintes": [("chomage", 2037, "<=", 0.5), ("pib", 2037, ">=", -1.0), ("modestes", 2037, ">=", -1.0),
                        ("decile_min", None, ">=", -1.5)],
    },
    "S5_global": {
        "libelle": "Optimisation globale (maximin des critères normalisés, sans pondération)",
        "objectif": "tchebychev",
        "contraintes": [("decile_min", None, ">=", -1.0)],
    },
}


def normalisation(var):
    """Échelle de chaque critère : écart interquantile (5 %-95 %) sur l'échantillon aléatoire à 10 ans."""
    X = echantillon(var, n=20_000, graine=1)
    Y = criteres_echantillon(var, X, 2037)
    for c in CRITERES:
        q = np.quantile(Y[c], [0.05, 0.95])
        NORM[c] = float(max(q[1] - q[0], 1e-6))


def main():
    exp = charger()
    n_rob = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    sortie = {"leviers": {k: {"bornes": [v[4], v[5]], "difficulte": v[6], "famille": v[7], "niveau": NIVEAU.get(k, "A"),
                              "experience_hausse": v[0], "experience_baisse": v[2]} for k, v in LEVIERS.items()},
              "criteres": {k: v[0] for k, v in CRITERES.items()}, "perimetres": {}}
    var_all = metamodele(exp)
    normalisation(var_all)            # même échelle pour tous les périmètres
    sortie["normalisation"] = dict(NORM)
    for per, niv in PERIMETRES.items():
        var = metamodele(exp, niv)
        P = {}
        X = echantillon(var)
        Y = criteres_echantillon(var, X, 2037)
        M = np.column_stack([Y[c] * CRITERES[c][1] for c in CRITERES])
        fr = pareto(M)
        P["pareto"] = {"portefeuilles": len(X), "non_domines": int(len(fr)), "part_dominee": float(1 - len(fr) / len(X))}
        for a, b in (("chomage", "dette"), ("modestes", "dette"), ("pib", "dette"), ("modestes", "chomage")):
            M2 = np.column_stack([Y[a] * CRITERES[a][1], Y[b] * CRITERES[b][1]])
            f2 = pareto(M2)
            P["pareto"][f"{a}|{b}"] = sorted([[float(Y[a][i]), float(Y[b][i])] for i in f2])
            # nuage (échantillon de 1 500 portefeuilles) pour les figures
            P["pareto"][f"nuage|{a}|{b}"] = [[float(Y[a][i]), float(Y[b][i])] for i in range(0, len(X), max(1, len(X) // 1500))]
        # front de Pareto exact à deux critères (méthode ε-contrainte, programme linéaire en nombres mixtes) : pour une
        # grille de niveaux du premier critère, meilleur niveau possible du second (au plus 8 leviers, pertes ≤ 1 % par décile)
        for a, b in (("chomage", "dette"), ("modestes", "dette"), ("pib", "dette"), ("modestes", "chomage")):
            sa, sb = CRITERES[a][1], CRITERES[b][1]
            xa = resoudre(var, {a: sa}, [("decile_min", None, ">=", -1.0)])
            xb = resoudre(var, {a: -sa}, [("decile_min", None, ">=", -1.0)])
            if xa is None or xb is None:
                continue
            ha, hb = evaluer(var, xa)[2037][a], evaluer(var, xb)[2037][a]
            pts = []
            for niv in np.linspace(min(ha, hb), max(ha, hb), 16):
                op = ">=" if sa > 0 else "<="
                x = resoudre(var, {b: sb}, [(a, 2037, op, float(niv)), ("decile_min", None, ">=", -1.0)])
                if x is not None:
                    e = evaluer(var, x)[2037]
                    pts.append([e[a], e[b], leviers_de(var, x)])
            P["pareto"][f"exact|{a}|{b}"] = pts
        strat = {}
        for nom, S in STRATEGIES.items():
            x = resoudre(var, S["objectif"], S["contraintes"], t_obj=S.get("t_obj", 2037), exclus=S.get("exclus", ()))
            if x is None:
                strat[nom] = {"libelle": S["libelle"], "erreur": "pas de solution"}
                continue
            strat[nom] = {"libelle": S["libelle"], "leviers": leviers_de(var, x), "metamodele": evaluer(var, x),
                          "objectif": S["objectif"], "contraintes": S["contraintes"], "exclus": S.get("exclus", [])}
            print(per, nom, strat[nom]["leviers"], {c: round(v, 2) for c, v in strat[nom]["metamodele"][2037].items()}, flush=True)
        P["strategies"] = strat
        if per == "principal":
            # robustesse aux préférences : poids aléatoires (simplexe), dette ≤ référence à 10 ans, pertes par décile ≤ 1 %
            rng = np.random.default_rng(2)
            freq, n_ok, sols = {}, 0, []
            for _ in range(n_rob):
                w = rng.dirichlet(np.ones(len(CRITERES)))
                obj = {c: wi * CRITERES[c][1] for c, wi in zip(CRITERES, w)}
                x = resoudre(var, obj, [("dette", 2037, "<=", 0.0), ("decile_min", None, ">=", -1.0)])
                if x is None:
                    continue
                n_ok += 1
                lv = leviers_de(var, x)
                sols.append({"poids": dict(zip(CRITERES, map(float, w))), "leviers": lv,
                             "criteres": {c: v for c, v in evaluer(var, x)[2037].items()}})
                for lev, v in lv.items():
                    k = f"{lev}|{'hausse' if v > 0 else 'baisse'}"
                    freq[k] = freq.get(k, 0) + 1
            P["robustesse_preferences"] = {"tirages_resolus": n_ok, "frequence": {k: v / max(n_ok, 1) for k, v in sorted(freq.items(), key=lambda z: -z[1])},
                                           "solutions": sols}
            print("robustesse", list(P["robustesse_preferences"]["frequence"].items())[:12], flush=True)
        # efficacité unitaire de chaque levier (par unité de borne) à 10 ans, pour le tableau des leviers
        P["efficacite"] = {f"{v[0]}|{'hausse' if v[1] > 0 else 'baisse'}": {"borne": v[2], **{c: v[3][2037][c] * v[2] for c in list(CRITERES) + EXTRAS}}
                           for v in var}
        sortie["perimetres"][per] = P
    sortie["strategies"] = sortie["perimetres"]["principal"]["strategies"]
    (RES / "optimisation_v07.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
