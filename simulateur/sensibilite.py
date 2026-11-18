"""Dispositif d'analyse de sensibilité (contre-expertise de novembre 2026, version 0.6).

Principe : pour un scénario (jeu de mesures), les exogènes de référence et de variante sont construites une fois par
`executer.construire` (microsimulation comprise), pour chaque niveau des facteurs qui agissent à la construction
(réactions des hauts revenus, élasticité du capital public). Les facteurs qui agissent dans le modèle bouclé
(coefficients estimés, paramètres calibrés, hypothèses) sont ensuite modifiés et seules deux simulations M8
(référence et variante, mêmes paramètres) sont refaites : environ 7 secondes par jeu de paramètres.

Approximations documentées (doc/13_contre_expertise.md) :
- les termes de calage de la trajectoire de référence sont ceux du jeu central : la référence est re-simulée avec les
  paramètres modifiés mais n'est pas re-calée (les écarts variante − référence sont peu sensibles au niveau de la
  référence, à vérifier au cas par cas) ;
- les rétroactions de la zone euro (M11) sont calculées une fois au jeu central puis appliquées avec un facteur
  d'échelle (facteur « europe ») ;
- le profil des propensions par décile est déformé linéairement autour de la moyenne (facteur « pmc_echelle » :
  0 = profil plat, 1 = profil central, 1,5 = profil accentué).

Catégories de paramètres (registre) : E estimé sur données françaises ; C calibré sur données françaises ;
L transposé de la littérature ; H hypothèse conventionnelle.
"""
from __future__ import annotations

import contextlib
import copy
import pathlib
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE))
import m7_equations as E  # noqa: E402
import m8_modele as M  # noqa: E402
import m14_heterogeneite as H14  # noqa: E402

# Facteurs : (nom, catégorie, cible, bas, central, haut, libellé, source)
# cible "eq:<équation>:<coef>" : coefficient estimé (bas/haut = ± 2 erreurs-types, renseignés à l'exécution)
FACTEURS = [
    ("conso_court_terme", "E", "eq:consommation:dlrdb", None, None, None, "Consommation : élasticité de court terme au revenu réel", "MCO 1997-2019, Eurostat"),
    ("conso_rappel", "E", "eq:consommation:ecart_1", None, None, None, "Consommation : force de rappel vers le revenu", "MCO 1997-2019"),
    ("import_demande", "E", "eq:importations:dld", None, None, None, "Importations : élasticité de court terme à la demande", "MCO 1997-2019"),
    ("import_prix", "E", "eq:importations:lprel_1", None, None, None, "Importations : élasticité-prix de long terme (numérateur)", "MCO 1997-2019"),
    ("export_prix", "E", "eq:exportations:dlprel", None, None, None, "Exportations : élasticité-prix", "MCO 1997-2019"),
    ("invest_accelerateur", "E", "eq:investissement_snf:dlq", None, None, None, "Investissement des SNF : accélérateur de court terme", "MCO 1997-2019"),
    ("invest_cout_capital", "E", "eq:investissement_snf:lcu_1", None, None, None, "Investissement des SNF : coût d'usage du capital", "MCO 1997-2019"),
    ("salaire_indexation", "E", "eq:salaires:dlpc", None, None, None, "Salaires : indexation de court terme sur les prix", "MCO 1997-2019"),
    ("salaire_rappel", "E", "eq:salaires:ecm_1", None, None, None, "Salaires : rappel vers la part salariale", "MCO 1997-2019"),
    ("prix_clu", "E", "eq:prix_va:dlclu", None, None, None, "Prix de valeur ajoutée : transmission du coût salarial unitaire", "panel 25 branches 1997-2019"),
    ("emploi_activite", "E", "eq:emploi:dlq", None, None, None, "Emploi : élasticité de court terme à la production", "panel 25 branches"),
    ("logement_revenu", "E", "eq:logement:dlrdb", None, None, None, "Logement des ménages : élasticité au revenu", "MCO 1997-2019"),
    ("theta_import", "E", "theta", 0.30, None, 0.70, "Transmission des prix d'importation (θ)", "MCO 1998-2024 (erreur-type ≈ 0,1)"),
    ("phillips", "C", "E.PHILLIPS", -0.008, -0.004, -0.002, "Courbe de Phillips (salaire / point de chômage)", "calibrée ; DG Trésor, Insee"),
    ("substitution", "L", "E.SIGMA_TRAVAIL", 0.2, 0.4, 0.7, "Élasticité de substitution capital-travail", "littérature (Cette et al.)"),
    ("fermeture_offre", "H", "rho", 0.0, M.RHO_DEFAUT, 0.4, "Fermeture d'offre (politique monétaire, crédit, compétitivité)", "hypothèse"),
    ("pmc_echelle", "L", "pmc", 0.0, 1.0, 1.5, "Hétérogénéité des propensions à consommer (0 plat, 1 central)", "littérature, Insee"),
    ("profits_distribues", "L", "distribution", 0.3, 0.5, 0.7, "Part des profits supplémentaires distribuée", "France Stratégie, littérature"),
    ("non_residents", "C", "non_residents", 0.20, 0.30, 0.50, "Part des dividendes versée aux non-résidents", "Banque de France"),
    ("comportements_hauts_revenus", "L", "construction:comportements", "basse", "centrale", "haute", "Réactions des hauts revenus (M13)", "littérature"),
    ("capital_public", "L", "construction:elasticite_capital_public", 0.04, 0.08, 0.12, "Élasticité de la production au capital public", "Bom et Ligthart (2014)"),
    ("europe", "H", "europe", 0.0, 1.0, 2.0, "Rétroactions zone euro (taux, demande des partenaires)", "M11, calibré"),
]
NOMS = [f[0] for f in FACTEURS]
INDICATEURS = ["pib", "croissance", "emploi", "chomage", "rdb", "c", "fbcf", "taux_epargne", "inflation", "pc", "solde_pib",
               "dette_pib", "solde_exterieur_pib", "rnb"]
EN_NIVEAU_DIFF = {"chomage", "taux_epargne", "solde_pib", "dette_pib", "solde_exterieur_pib", "croissance", "inflation"}
ANNEES = (2027, 2028, 2030, 2032)


# Contraintes de signe imposées par la théorie (stabilité des mécanismes à correction d'erreur, élasticités-prix
# négatives). Plusieurs intervalles à ± 2 erreurs-types les franchissent : les données annuelles (23 observations) ne
# permettent pas de rejeter l'absence de ces mécanismes. Les intervalles sont tronqués à ces bornes (signalé dans le
# rapport) ; les tirages statistiques qui les violent sont écartés et comptés.
SIGNES = {("consommation", "ecart_1"): (None, -0.02), ("salaires", "ecm_1"): (None, -0.02), ("logement", "ecart_1"): (None, -0.02),
          ("importations", "lm_1"): (None, -0.05), ("investissement_snf", "ecm_1"): (None, -0.02), ("prix_va", "ecm_1"): (None, -0.02),
          ("emploi", "ecm_1"): (None, -0.02), ("importations", "dlprel"): (None, 0.0), ("importations", "lprel_1"): (None, 0.0),
          ("exportations", "dlprel"): (None, 0.0), ("investissement_snf", "lcu_1"): (None, 0.0), ("salaires", "dlpc"): (0.0, 1.0),
          ("consommation", "dlrdb"): (0.0, 1.2), ("logement", "dlrdb"): (0.0, None)}


def _tronquer(eq, coef, x):
    lo, hi = SIGNES.get((eq, coef), (None, None))
    if lo is not None:
        x = max(lo, x)
    if hi is not None:
        x = min(hi, x)
    return x


def bornes(mod, brutes=False):
    """Bornes des facteurs : coefficients estimés ± 2 erreurs-types (intervalle de confiance à 95 % environ), tronqués aux
    contraintes de signe (sauf si `brutes`)."""
    out = {}
    for nom, cat, cible, b, c, h, *_ in FACTEURS:
        if cible.startswith("eq:"):
            _, eq, coef = cible.split(":")
            r = mod.eq[eq].res
            v, se = float(r.params[coef]), float(r.bse[coef])
            lo, hi = v - 2 * se, v + 2 * se
            if not brutes:
                lo, hi = _tronquer(eq, coef, lo), _tronquer(eq, coef, hi)
            out[nom] = (lo, v, hi)
        elif cible == "theta":
            out[nom] = (b, float(mod.theta), h)
        else:
            out[nom] = (b, c, h)
    return out


class Preparation:
    """Exogènes d'un scénario préparées une fois (référence, variantes selon les facteurs de construction)."""

    def __init__(self, scenario, mod=None):
        from simulateur import executer as X
        import m11_europe as EU
        self.X, self.scenario = X, X.depuis_curseurs(copy.deepcopy(scenario))
        self.mod = mod or X.modele(2022)
        H0 = self.scenario.setdefault("hypotheses", {})
        self.var = {}
        for comp in ("basse", "centrale", "haute"):
            for kg in (0.04, 0.08, 0.12):
                if comp != "centrale" and kg != 0.08:
                    continue
                sc = copy.deepcopy(self.scenario)
                sc["hypotheses"].update({"comportements": comp, "elasticite_capital_public": kg})
                ref, var, ans, info = X.construire(sc, self.mod)
                self.var[(comp, kg)] = var
                if comp == "centrale" and kg == 0.08:
                    self.ref, self.ans, self.info = ref, ans, info
        # rétroactions zone euro au jeu central
        c, v, Eu = EU.simuler_couple(self.mod, self.ans, self.ref, self.var[("centrale", 0.08)], theta=H0.get("prime_risque", EU.THETA_PRIME))
        self.eu = Eu
        mm = self.var[("centrale", 0.08)].mesure_menages or {}
        self.conso_central = float(mm.get("conso", 0.0)) if mm else 0.0

    def exogenes(self, v):
        """Exogènes (référence, variante) pour un jeu de facteurs `v` (dictionnaire nom → valeur)."""
        comp = v.get("comportements_hauts_revenus", "centrale")
        kg = v.get("capital_public", 0.08)
        if (comp, kg) not in self.var:
            # combinaisons non préparées : réactions et capital public pris séparément (additivité, voir doc)
            kg = 0.08 if comp != "centrale" else kg
        var = copy.deepcopy(self.var[(comp, kg)])
        ref = copy.deepcopy(self.ref)
        lam = float(v.get("europe", 1.0))
        if self.eu is not None and lam:
            var.taux_long = var.taux_long.add(lam * self.eu.taux_long_fr, fill_value=0.0)
            var.demande_mondiale = var.demande_mondiale * (1 + lam * self.eu.demande_ue.reindex(var.demande_mondiale.index).fillna(0.0) / 100)
        if var.mesure_menages:
            mm = dict(var.mesure_menages)
            mm["conso"] = float(mm.get("conso", 0.0)) * float(v.get("pmc_echelle", 1.0))
            var.mesure_menages = mm
        return ref, var


DEBUT_ALTERNATIF = 2026   # première année projetée : les paramètres modifiés s'appliquent à partir de cette année


def alternatifs(mod, v, coefs=None):
    """Paramètres alternatifs transmis au modèle (Exogenes.parametres_alternatifs), appliqués à partir de 2026 : la période
    observée 2023-2025 reste reproduite et l'ancrage des termes de rappel neutralise les sauts de niveau d'équilibre.
    (Version initiale du dispositif : paramètres modifiés dès 2023 sans recalage, d'où une dérive artificielle de la
    référence, explosive pour l'élasticité de substitution ; voir doc/13_contre_expertise.md, section 4.)"""
    params = {}
    for k, p in (coefs or {}).items():
        params[k] = p.copy()
    for nom, cat, cible, *_ in FACTEURS:
        if nom in v and cible.startswith("eq:"):
            _, eq, coef = cible.split(":")
            params.setdefault(eq, mod.eq[eq].res.params.copy())[coef] = float(v[nom])
    alt = {"debut": DEBUT_ALTERNATIF, "params": params}
    if "phillips" in v:
        alt["phillips"] = float(v["phillips"])
    if "substitution" in v:
        alt["sigma"] = float(v["substitution"])
    if "theta_import" in v:
        alt["theta"] = float(v["theta_import"])
    if "fermeture_offre" in v:
        alt["rho"] = float(v["fermeture_offre"])
    return alt


@contextlib.contextmanager
def parametres(mod, v, coefs=None):
    """Applique temporairement les facteurs propres aux mesures (M14 : propensions, distribution des profits,
    non-résidents) ; les paramètres du modèle bouclé passent par `alternatifs`."""
    s_mod = (E.PHILLIPS, E.SIGMA_TRAVAIL, H14.DISTRIBUTION_PROFITS["central"], H14.PART_NON_RESIDENTS, H14.PMC_TOP1)
    try:
        if "profits_distribues" in v:
            H14.DISTRIBUTION_PROFITS["central"] = float(v["profits_distribues"])
        if "non_residents" in v:
            H14.PART_NON_RESIDENTS = float(v["non_residents"])
        if "pmc_echelle" in v:
            moy = H14.pmc_moyenne("central")
            H14.PMC_TOP1 = moy + float(v["pmc_echelle"]) * (s_mod[4] - moy)
        yield
    finally:
        E.PHILLIPS, E.SIGMA_TRAVAIL, H14.DISTRIBUTION_PROFITS["central"], H14.PART_NON_RESIDENTS, H14.PMC_TOP1 = s_mod


def ecarts(mod, c, v):
    from simulateur import executer as X
    out = {}
    for d in (c, v):
        pib1 = pd.concat([pd.Series({mod.B: float(mod.macro.pib[mod.B])}), d.pib])
        pc1 = pd.concat([pd.Series({mod.B: float(mod.macro.p_c[mod.B])}), d.pc])
        d["croissance"] = (pib1 / pib1.shift(1) - 1).reindex(d.index) * 100
        d["inflation"] = (pc1 / pc1.shift(1) - 1).reindex(d.index) * 100
        d["solde_exterieur_pib"] = d.solde_exterieur / d.pib_nominal * 100
    for k in INDICATEURS:
        out[k] = {}
        for t in ANNEES:
            if t not in v.index:
                continue
            if k == "emploi":
                out[k][t] = float(v[k][t] - c[k][t])
            elif k in EN_NIVEAU_DIFF:
                out[k][t] = float(v[k][t] - c[k][t])
            else:
                out[k][t] = float((v[k][t] / c[k][t] - 1) * 100)
    return out


def evaluer(prep, v, coefs=None):
    """Écarts variante − référence pour un jeu de facteurs."""
    mod = prep.mod
    ref, var = prep.exogenes(v)
    if any(n in v for n in NOMS if n not in ("profits_distribues", "non_residents", "pmc_echelle", "comportements_hauts_revenus",
                                             "capital_public", "europe")) or coefs:
        alt = alternatifs(mod, v, coefs)
        ref.parametres_alternatifs = var.parametres_alternatifs = alt
    with parametres(mod, v, coefs):
        c = mod.simuler(prep.ans, ref)
        w = mod.simuler(prep.ans, var)
    return ecarts(mod, c, w)


# ---------------------------------------------------------------- méthodes

def morris(prep, r=6, niveaux=4, graine=1):
    """Criblage de Morris (Morris 1991 ; Campolongo, Cariboni et Saltelli 2007) : r trajectoires de k+1 points sur une
    grille à `niveaux` niveaux ; effets élémentaires EE = Δy / Δx normalisé (x dans [0, 1]). Renvoie la liste des
    évaluations et, par indicateur × année × facteur : μ* (moyenne des |EE|), μ, σ."""
    rng = np.random.default_rng(graine)
    B = bornes(prep.mod)
    k = len(FACTEURS)
    delta = niveaux / (2 * (niveaux - 1))
    grille = np.arange(niveaux) / (niveaux - 1)

    def valeur(i, x):
        nom, cat, cible, *_ = FACTEURS[i]
        b, c, h = B[nom]
        if isinstance(b, str):           # facteur discret à trois niveaux
            return [b, c, h][min(2, int(round(x * 2)))]
        if nom == "capital_public":
            return [b, c, h][min(2, int(round(x * 2)))]
        return b + x * (h - b)

    evals, EE = [], {}
    for _ in range(r):
        x = rng.choice(grille[: niveaux // 2], size=k)          # point de départ tel que x + Δ ≤ 1
        ordre = rng.permutation(k)
        sgn = np.ones(k)
        pts = [x.copy()]
        for i in ordre:
            x = x.copy()
            x[i] += delta * sgn[i]
            pts.append(x)
        ys = []
        for p in pts:
            v = {FACTEURS[i][0]: valeur(i, p[i]) for i in range(k)}
            y = evaluer(prep, v)
            ys.append(y)
            evals.append({"x": p.tolist(), "valeurs": v, "y": y})
        for j, i in enumerate(ordre):
            for ind in INDICATEURS:
                for t in ANNEES:
                    if t not in ys[j][ind]:
                        continue
                    d = (ys[j + 1][ind][t] - ys[j][ind][t]) / delta
                    EE.setdefault((ind, t, FACTEURS[i][0]), []).append(d)
    stats = {}
    for (ind, t, nom), L in EE.items():
        L = np.array(L, dtype=float)
        f = L[np.isfinite(L)]
        stats.setdefault(ind, {}).setdefault(t, {})[nom] = {
            "mu_etoile": float(np.abs(f).mean()) if len(f) else float("nan"), "mu": float(f.mean()) if len(f) else float("nan"),
            "sigma": float(f.std(ddof=1)) if len(f) > 1 else 0.0, "n": int(len(f)), "non_finis": int(len(L) - len(f))}
    return evals, stats


def univarie(prep):
    """Un facteur à la fois, aux bornes basse et haute, les autres au centre."""
    B = bornes(prep.mod)
    out = {}
    for nom, *_ in FACTEURS:
        b, c, h = B[nom]
        out[nom] = {"bas": evaluer(prep, {nom: b}), "haut": evaluer(prep, {nom: h}), "valeurs": (b, c, h)}
    return out


def tirages_statistiques(mod, n=60, graine=7):
    """Tirages conjoints des coefficients des équations estimées, loi normale multivariée de moyenne les estimations et de
    covariance la matrice de covariance des MCO (incertitude d'estimation seulement ; n'inclut pas l'incertitude de
    spécification)."""
    rng = np.random.default_rng(graine)
    eqs = [k for k, e in mod.eq.items() if hasattr(e.res, "cov_params") and k not in ("transmission",)]
    out, rejets = [], 0
    while len(out) < n:
        d, ok = {}, True
        for k in eqs:
            r = mod.eq[k].res
            mu, cov = r.params.values, np.asarray(r.cov_params())
            d[k] = pd.Series(rng.multivariate_normal(mu, cov, method="cholesky" if np.all(np.linalg.eigvalsh(cov) > 0) else "svd"), index=r.params.index)
            for (e_, c_), (lo, hi) in SIGNES.items():
                if e_ == k and ((lo is not None and d[k][c_] < lo) or (hi is not None and d[k][c_] > hi)):
                    ok = False
        if ok:
            out.append(d)
        else:
            rejets += 1
        if rejets > 50 * n:
            break
    tirages_statistiques.rejets = rejets
    return out


def scenarios_coherents(prep):
    """Jeux d'hypothèses économiquement cohérents (pas de combinaison contradictoire)."""
    B = bornes(prep.mod)
    lo = {n: B[n][0] for n in NOMS}
    hi = {n: B[n][2] for n in NOMS}
    S = {
        "central": {},
        "demande forte (keynésien)": {"fermeture_offre": 0.0, "phillips": hi["phillips"], "conso_court_terme": hi["conso_court_terme"],
                                      "pmc_echelle": 1.5, "import_demande": lo["import_demande"], "europe": 0.0},
        "offre contrainte (classique)": {"fermeture_offre": 0.4, "phillips": lo["phillips"], "conso_court_terme": lo["conso_court_terme"],
                                         "salaire_indexation": hi["salaire_indexation"], "prix_clu": hi["prix_clu"], "europe": 2.0},
        "économie très ouverte": {"import_demande": hi["import_demande"], "import_prix": lo["import_prix"], "export_prix": lo["export_prix"],
                                  "non_residents": 0.50},
        "réactions fortes des ménages aisés et des entreprises": {"comportements_hauts_revenus": "haute", "profits_distribues": 0.7,
                                                                   "pmc_echelle": 1.5, "invest_cout_capital": lo["invest_cout_capital"]},
        "réactions faibles": {"comportements_hauts_revenus": "basse", "profits_distribues": 0.3, "pmc_echelle": 0.0,
                              "invest_cout_capital": hi["invest_cout_capital"]},
    }
    return {k: evaluer(prep, v) for k, v in S.items()}, S
