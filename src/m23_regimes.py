"""M23 — Environnement, régimes de politique économique et programmes (phase 5, lot 5.0).

Toute simulation = Environnement × Régime × Programme :
  - Environnement : modèle (configuration SPEC), exogènes de la référence calibrées une seule fois (recalage 2023-2025,
    FMI 2026-2031, hypothèses de long terme, termes de calage) pour une convention de dépense donnée ; mis en cache.
  - Régime : règle budgétaire (aucune, stabilisation de la dette, ajustement progressif), politique monétaire (taux
    exogènes ; règle BCE au lot 5.2), jeu de paramètres fragiles. Appliqué SANS recalibrer l'environnement.
  - Programme : mesures (fonction qui modifie une copie des exogènes).

Effet d'un programme : Δ(P | E, R) = Y(E, R, P) − Y(E, R, ∅). Par défaut la règle budgétaire est FIGÉE : la trajectoire
d'effort calculée sur la référence (E, R, ∅) est imposée telle quelle à la simulation avec programme (le coût du
programme n'est pas compensé). Mode ACTIF : la règle réagit aussi au programme.

Règle budgétaire (note 22, § 1.3), en points de PIB, calculée au début de l'année t avec les seules années < t :
  s       = solde primaire − ε × écart de production (solde primaire ajusté du cycle)
  s̄_t     = (r̄ − ḡ) / (1 + ḡ) × d_{t−1}            r̄ : taux apparent, ḡ : croissance nominale du PIB potentiel,
                                                     moyennes des 3 dernières années
  s*_t    = s̄_t (stabilisation) ;  s̄_t + β (d_{t−1} − d*) (ajustement progressif)
  Δe_t    = clip(α (s*_t − s_{t−1}), plancher, plafond) ; 0 si écart de production < −écart_suspension
            plancher = 0 (asymétrique, central) ou −plafond (symétrique, variante)
  e_t     = e_{t−1} + Δe_t   (effort ex ante cumulé, réparti entre instruments selon `parts`)
"""
from __future__ import annotations

import copy
import hashlib
import json
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import m7_equations as E
import m8_modele as M8
import m8_reference as RF

INSTRUMENTS = ("conso_publique", "prestations", "impots_menages", "impots_produits")


# ------------------------------------------------------------------------------------------------------------- régimes
@dataclass
class RegleBudgetaire:
    type: str = "aucune"                   # "aucune" | "stabilisation" | "ajustement"
    debut: int = 2027
    alpha: float = 0.5
    beta: float = 0.02
    dette_cible: float = 90.0              # % du PIB (seuil de la clause de sauvegarde de la dette, règles UE 2024)
    plafond: float = 0.5                   # point de PIB par an
    symetrique: bool = False               # True : l'effort peut aussi diminuer (plancher = −plafond)
    ecart_suspension: float = 1.5          # clause d'écart : pas d'effort si écart de production < −1,5 point
    epsilon: float = 0.5                   # semi-élasticité du solde au cycle (ordre de grandeur UE)
    parts: dict = field(default_factory=lambda: {"conso_publique": 0.30, "prestations": 0.20,
                                                 "impots_menages": 0.30, "impots_produits": 0.20})
    mode: str = "figee"                    # "figee" | "active" (pour l'évaluation des programmes)

    def __post_init__(self):
        assert self.type in ("aucune", "stabilisation", "ajustement"), self.type
        assert self.mode in ("figee", "active"), self.mode
        assert abs(sum(self.parts.values()) - 1) < 1e-9 and set(self.parts) <= set(INSTRUMENTS)


from m24_monetaire import RegimeMonetaire as ReglesMonetaire, AppliqueurMonetaire  # noqa: E402  (lot 5.2)


# Jeux de paramètres fragiles applicables sans réestimation ni recalibration (note 22, § 3.3). σ et le partage
# prix-marges demandent une autre configuration du modèle (réestimation) : ils relèvent de l'environnement.
JEUX_PARAMETRES = {
    "central": {},
    "ancrage_faible": {"phillips": 2.0, "kappa_prix": 2.0},
    "ancrage_fort": {"phillips": 0.5, "kappa_prix": 0.5},
    # lot 5.3 : retour au potentiel (paramètre le plus influent à moyen terme, rapport 21 § 5.5)
    "fermeture_lente": {"fermeture_rho": 0.1},
    "fermeture_rapide": {"fermeture_rho": 0.3},
    "fermeture_chomage": {"fermeture_mode": "chomage", "fermeture_rho": 0.15},
}


@dataclass
class Regime:
    budgetaire: RegleBudgetaire = field(default_factory=RegleBudgetaire)
    monetaire: ReglesMonetaire = field(default_factory=ReglesMonetaire)
    parametres: str = "central"
    nom: str = ""

    def __post_init__(self):
        assert self.parametres in JEUX_PARAMETRES, self.parametres

    def description(self) -> dict:
        return {"nom": self.nom, "budgetaire": dict(vars(self.budgetaire)), "monetaire": dict(vars(self.monetaire)), "parametres": self.parametres}


def regime(code: str, monetaire: dict | str | None = None, **kw) -> Regime:
    """Régimes nommés : R0 (aucune règle), R1 (stabilisation), R2 (ajustement progressif, central), R2_actif, R2_sym.
    `monetaire` : "exogene" (défaut), "bce" (règle de la BCE, prime souveraine estimée en écart à la référence), ou dict
    d'arguments de RegimeMonetaire."""
    base = {"R0": dict(type="aucune"), "R1": dict(type="stabilisation"), "R2": dict(type="ajustement"),
            "R2_actif": dict(type="ajustement", mode="active"), "R2_sym": dict(type="ajustement", symetrique=True)}[code]
    par = kw.pop("parametres", "central")
    if monetaire is None or monetaire == "exogene":
        mon = ReglesMonetaire()
    elif monetaire == "bce":
        mon = ReglesMonetaire(type="bce", prime="ecart_reference")
    else:
        mon = ReglesMonetaire(**monetaire)
    return Regime(budgetaire=RegleBudgetaire(**{**base, **kw}), monetaire=mon, parametres=par,
                  nom=code + ("" if mon.type == "exogene" and mon.prime == "aucune" else f"+{mon.type}"))


REGIME_PRINCIPAL = "R2"


# ------------------------------------------------------------------------------------------------------- programmes
@dataclass
class Programme:
    nom: str = "aucun"
    appliquer: object = None               # fonction (modele, exogenes) -> None, modifie la copie des exogènes
    description: str = ""


PROGRAMME_NUL = Programme()


# ---------------------------------------------------------------------------------------------------- environnement
CONFIGURATIONS = {"p4": M8.configurer_phase4, "v09": M8.configurer_v09, "v08": M8.configurer_v08}


class Environnement:
    """Modèle + exogènes de référence calibrées (cache disque de m8_reference). Construit une seule fois par
    (configuration, convention de dépense, base, horizon)."""

    def __init__(self, conf, convention, mod, R, fin):
        self.conf, self.convention, self.mod, self.R, self.fin = conf, convention, mod, R, fin
        self.annees = list(R["trajectoire"].index)
        self.reference = R["trajectoire"]               # trajectoire R0 (sans règle)
        self.spec = dict(M8.SPEC)
        self.sigma = E.SIGMA_TRAVAIL

    @classmethod
    def charger(cls, conf="p4", convention="part_constante", base=2022, fin=2047):
        M8.configurer_v08()
        CONFIGURATIONS[conf]()
        mod = M8.Modele(base)
        R = RF.compte_reference(mod, range(base + 1, fin + 1), journal=lambda *a: None, convention=convention)
        return cls(conf, convention, mod, R, fin)

    def reference_monetaire(self, taux_court_reference="observe") -> pd.DataFrame:
        """Trajectoire R0 à taux exogènes (même trajectoire exogène du taux directeur) : base des écarts auxquels réagissent
        la BCE et la prime souveraine. Mise en cache (une simulation)."""
        cle = "_refmon_" + taux_court_reference
        if not hasattr(self, cle):
            reg = Regime(monetaire=ReglesMonetaire(taux_court_reference=taux_court_reference), nom="R0")
            setattr(self, cle, simuler(self, reg)["trajectoire"])
        return getattr(self, cle)

    def activer(self):
        """Rétablit la configuration du modèle de l'environnement (SPEC, σ) avant toute simulation."""
        M8.SPEC.update(self.spec)
        E.SIGMA_TRAVAIL = self.sigma

    def empreinte(self) -> str:
        return hashlib.sha1(json.dumps([self.conf, self.convention, self.spec, self.sigma, self.R["empreinte"]], sort_keys=True,
                                       default=str).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------------- application de la règle budgétaire
class AppliqueurBudgetaire:
    """Calcule (mode règle) ou impose (mode figé) l'effort e_t et le traduit en mesures sur les leviers de M8.
    Enregistre pour chaque année : effort ex ante total et par instrument, cible, solde stabilisant."""

    def __init__(self, regle: RegleBudgetaire, mod, effort_impose: dict | None = None):
        self.r, self.mod = regle, mod
        self.effort_impose = effort_impose
        self.e = {}
        self.journal = {}
        B = mod.B
        # part de la consommation publique dans le PIB, aux prix courants de l'année de base (comptes nationaux). Une
        # première version rapportait la consommation publique du TES à la VA aux prix de base (0,30 au lieu de 0,24) :
        # l'effort réalisé par cet instrument était sous-estimé d'un cinquième (corrigé, test d'effort ex ante).
        self.part_g = float(mod.macro.g_cp[B] / mod.macro.pib_cp[B])
        self.part_d2 = float(mod.apu.d2rec[B] / mod.macro.pib_cp[B])
        self.part_c = float(mod.macro.c_cp[B] / mod.macro.pib_cp[B])
        self._g0 = None

    def _calculer(self, t, res):
        r = self.r
        if r.type == "aucune" or t < r.debut:
            return 0.0, {}
        h = pd.DataFrame(res).set_index("annee")
        if t - 1 not in h.index or t - 3 not in h.index:
            return self.e.get(t - 1, 0.0), {}
        y = h.loc[t - 1]
        d = float(y.dette_pib)
        sp = float(y.solde_pib + 100 * y.interets / y.pib_nominal)          # solde primaire
        s = sp - r.epsilon * float(y.ecart_production)                     # ajusté du cycle
        a = [t - 3, t - 2, t - 1]
        rbar = float(np.mean([h.loc[x, "taux_apparent"] for x in a])) / 100
        gpot = [np.log(h.loc[x, "pib_potentiel"] / h.loc[x - 1, "pib_potentiel"]) + np.log(h.loc[x, "pc"] / h.loc[x - 1, "pc"])
                for x in a if x - 1 in h.index]
        gbar = float(np.exp(np.mean(gpot)) - 1) if gpot else 0.0
        sbar = (rbar - gbar) / (1 + gbar) * d
        cible = sbar + (r.beta * (d - r.dette_cible) if r.type == "ajustement" else 0.0)
        plancher = -r.plafond if r.symetrique else 0.0
        de = float(np.clip(r.alpha * (cible - s), plancher, r.plafond))
        suspendu = float(y.ecart_production) < -r.ecart_suspension
        if suspendu:
            de = 0.0
        e = max(self.e.get(t - 1, 0.0) + de, 0.0) if not r.symetrique else self.e.get(t - 1, 0.0) + de
        return e, {"dette_t_1": d, "solde_primaire_ajuste_t_1": s, "r_bar": 100 * rbar, "g_bar": 100 * gbar,
                   "solde_stabilisant": sbar, "cible": cible, "delta_effort": e - self.e.get(t - 1, 0.0), "suspendu": suspendu}

    def __call__(self, mod, ex, t, res):
        if self._g0 is None:
            self._g0 = ex.conso_publique.copy()
        if self.effort_impose is not None:
            e, info = float(self.effort_impose.get(t, 0.0)), {"impose": True}
        else:
            e, info = self._calculer(t, res)
        self.e[t] = e
        p = self.r.parts
        ins = {k: e * p.get(k, 0.0) for k in INSTRUMENTS}
        self.journal[t] = {"effort": e, **{f"effort_{k}": v for k, v in ins.items()}, **info}
        if e == 0.0 and not self.e.get(t - 1):
            return
        B = mod.B
        pibB = float(mod.macro.pib_cp[B])
        # 1. consommation publique (volume) : −x points de PIB, à part de la consommation publique de base
        ex.conso_publique[t] = float(self._g0[t]) * (1 - ins["conso_publique"] / 100 / self.part_g)
        # 2. prestations (M€ courants) : −x points du PIB nominal de l'année précédente
        pibn_1 = float(pd.DataFrame(res).set_index("annee").pib_nominal.get(t - 1, pibB)) if res else pibB
        aj = ex.ajust_prestations.copy() if ex.ajust_prestations is not None else pd.Series(dtype=float)
        base_aj = self._aj0.get(t, 0.0) if hasattr(self, "_aj0") else None
        if base_aj is None:
            self._aj0 = {k: float(v) for k, v in aj.items()}
            base_aj = self._aj0.get(t, 0.0)
        aj[t] = base_aj - ins["prestations"] / 100 * pibn_1
        ex.ajust_prestations = aj.sort_index()
        # 3. impôts des ménages : points de PIB (mécanisme `impots_menages_pib` de M8)
        niv = ex.niveaux if ex.niveaux is not None else {}
        if not hasattr(self, "_niv0"):
            self._niv0 = {k: (v.copy() if isinstance(v, pd.Series) else v) for k, v in niv.items()}
        def poser(cle, val):
            s0 = self._niv0.get(cle)
            base = float(s0.get(t, 0.0)) if isinstance(s0, pd.Series) else 0.0
            s = niv.get(cle)
            s = (s.copy() if isinstance(s, pd.Series) else pd.Series(dtype=float))
            s[t] = base + val
            niv[cle] = s.sort_index()
        poser("impots_menages_pib", ins["impots_menages"])
        # 4. impôts sur les produits : variation relative des recettes, répercussion de 90 % sur les prix à la consommation
        poser("impots_produits", ins["impots_produits"] / 100 / self.part_d2)
        poser("prix_conso", 0.9 * ins["impots_produits"] / 100 / self.part_c)
        ex.niveaux = niv


# --------------------------------------------------------------------------------------------------------- simulation
def _appliquer_parametres(jeu: str, ex):
    p = JEUX_PARAMETRES[jeu]
    sauv = (E.PHILLIPS,)
    if "phillips" in p:
        E.PHILLIPS = sauv[0] * p["phillips"]
    if "kappa_prix" in p:
        ex.kappa_prix = M8.KAPPA_PRIX * p["kappa_prix"]
    if "fermeture_rho" in p:
        ex.fermeture_offre = p["fermeture_rho"]
    if "fermeture_mode" in p:
        ex.fermeture_mode = p["fermeture_mode"]
    return sauv


# Variantes d'environnement appliquées après calibration (hypothèses exogènes alternatives, sans recalibration). À
# n'utiliser que si l'écart induit aux cibles de calage est négligeable (vérifié dans phase5/audit_taux_composition.py).
def _taux_court_observe():
    """Euribor 3 mois (Eurostat irt_st_m, zone euro) : moyenne mensuelle de 2026 (janvier-octobre) et dernier mois
    observé (octobre 2026), maintenu ensuite — même convention que l'OAT dans la référence."""
    from telechargement import telecharger
    f = telecharger("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/irt_st_m?geo=EA&int_rt=IRT_M3"
                    "&sinceTimePeriod=2025-01&format=JSON&lang=en", "eurostat_irt_st_m_EA_2026_11.json")
    d = json.loads(f.read_text())
    inv = {i: k for k, i in d["dimension"]["time"]["category"]["index"].items()}
    obs = sorted((inv[int(k)], float(v)) for k, v in d["value"].items())
    m26 = [v for k, v in obs if k.startswith("2026")]
    return float(np.mean(m26)), obs[-1]


def variante_taux_court_observe(debut=2026):
    """Corrige le taux court de la référence : M8 le déduisait du taux long moins l'écart moyen 2018-2022 (0,76 pt),
    soit 4,13 % avec l'OAT à 4,89 %, contre 2,63 % observé (Euribor 3 mois, octobre 2026)."""
    moy26, (mois, dernier) = _taux_court_observe()
    import m17_dette as D
    _lt, st = D.taux_observes()

    def f(mod, ex):
        idx = sorted(set(ex.taux_long.index))
        ex.taux_court = pd.Series({t: (float(st[t]) if t in st.index and t < debut else (moy26 if t == 2026 else dernier)) for t in idx})
    f.description = f"taux court observé (2026 : {moy26:.2f} %, puis {dernier:.2f} %, {mois}) à partir de {debut}"
    return f


def variante_oat(cible=3.82, debut=2027, fin_convergence=2029, avec=None):
    """OAT convergeant linéairement de son niveau de 2026 vers `cible` (défaut : moyenne des 12 derniers mois observés,
    novembre 2025-octobre 2026) entre `debut` et `fin_convergence`, constante ensuite. `avec` : variante appliquée avant."""
    def f(mod, ex):
        if avec is not None:
            avec(mod, ex)
        tl = ex.taux_long.copy().astype(float)
        x0 = float(tl[debut - 1])
        for t in tl.index:
            if t >= debut:
                k = min(1.0, (t - debut + 1) / (fin_convergence - debut + 1))
                tl[t] = x0 + k * (cible - x0)
        ex.taux_long = tl
    f.description = f"OAT vers {cible} % en {fin_convergence}"
    return f


def simuler(env: Environnement, reg: Regime, prog: Programme = PROGRAMME_NUL, effort_impose: dict | None = None,
            variante_env=None) -> dict:
    """Une simulation (E, R, P). Ne recalibre jamais l'environnement. Renvoie la trajectoire (avec colonnes « imposé »
    et « produit »), l'effort budgétaire et la durée. `variante_env` : hypothèse exogène alternative (fonction)."""
    t0 = time.time()
    env.activer()
    ex = copy.deepcopy(env.R["exogenes"])
    if variante_env is not None:
        variante_env(env.mod, ex)
    if prog.appliquer is not None:
        prog.appliquer(env.mod, ex)
    sauv = _appliquer_parametres(reg.parametres, ex)
    app = AppliqueurBudgetaire(reg.budgetaire, env.mod, effort_impose)
    m = reg.monetaire
    besoin_ref = m.type == "bce" or m.prime == "ecart_reference"
    ref_m = env.reference_monetaire(m.taux_court_reference) if besoin_ref else None
    mon = AppliqueurMonetaire(m, env.mod, env.R["exogenes"], ref_m)

    def crochet(mod, ex_, t, res):
        mon(mod, ex_, t, res)
        app(mod, ex_, t, res)
    ex.regime_hook = crochet
    try:
        r = env.mod.simuler(env.annees, ex)
    finally:
        E.PHILLIPS = sauv[0]
    j = pd.DataFrame(app.journal).T.reindex(r.index)
    for k in ["effort"] + [f"effort_{i}" for i in INSTRUMENTS]:
        r["impose_" + k] = j[k].astype(float).fillna(0.0) if k in j else 0.0
    r["solde_primaire_pib"] = r.solde_pib + 100 * r.interets / r.pib_nominal
    jm = pd.DataFrame(mon.journal).T.reindex(r.index)
    for k in ("taux_directeur", "ecart_directeur", "ecart_bund", "ecart_souverain", "oat", "ecart_credit_menages", "ecart_credit_entreprises"):
        r["mon_" + k] = jm[k].astype(float) if k in jm else np.nan
    return {"trajectoire": r, "effort": dict(app.e), "journal": app.journal, "duree_s": time.time() - t0,
            "regime": reg.description(), "programme": prog.nom, "environnement": env.empreinte()}


def evaluer(env: Environnement, reg: Regime, prog: Programme, ref: dict | None = None, variante_env=None) -> dict:
    """Effet d'un programme dans un régime : Y(E, R, P) − Y(E, R, ∅). Règle figée : l'effort de la référence (E, R, ∅)
    est imposé à la simulation avec programme. Renvoie référence, variante et écarts."""
    ref = ref or simuler(env, reg, variante_env=variante_env)
    impose = ref["effort"] if reg.budgetaire.mode == "figee" else None
    var = simuler(env, reg, prog, effort_impose=impose, variante_env=variante_env)
    a, b = var["trajectoire"], ref["trajectoire"]
    ecart = pd.DataFrame({
        "PIB (%)": 100 * np.log(a.pib / b.pib), "emploi (milliers)": a.emploi - b.emploi, "chômage (pt)": a.chomage - b.chomage,
        "prix (%)": 100 * np.log(a.pc / b.pc), "solde (pt PIB)": a.solde_pib - b.solde_pib, "dette (pt PIB)": a.dette_pib - b.dette_pib,
        "effort imposé (pt PIB)": a.impose_effort - b.impose_effort})
    return {"reference": ref, "variante": var, "ecart": ecart}


# ------------------------------------------------------------------------------------------- robustesse (lot 5.3)
REGIMES_ROBUSTESSE = {
    "principal (R2 figé, taux exogènes, central)": dict(code="R2"),
    "sans règle budgétaire (R0)": dict(code="R0"),
    "stabilisation (R1)": dict(code="R1"),
    "R2 active symétrique": dict(code="R2_sym", mode="active"),
    "R2 + BCE et prime": dict(code="R2", monetaire="bce"),
    "R2, ancrage faible": dict(code="R2", parametres="ancrage_faible"),
    "R2, ancrage fort": dict(code="R2", parametres="ancrage_fort"),
    "R2, fermeture lente": dict(code="R2", parametres="fermeture_lente"),
    "R2, fermeture rapide": dict(code="R2", parametres="fermeture_rapide"),
    "R2, fermeture sur le chômage": dict(code="R2", parametres="fermeture_chomage"),
}


def robustesse(env: Environnement, prog: Programme, horizons=(5, 15), debut=2027, regimes: dict | None = None) -> pd.DataFrame:
    """Tableau de robustesse d'un programme : effet (programme − référence du même régime) dans chaque régime, aux
    horizons donnés (années après `debut`). Les paramètres structurels qui exigent un autre environnement (σ, équation
    des prix de VA) ne sont pas couverts ici (environnements distincts, à calibrer une fois)."""
    regimes = regimes or REGIMES_ROBUSTESSE
    rows = {}
    for nom, k in regimes.items():
        kk = dict(k); code = kk.pop("code")
        e = evaluer(env, regime(code, **kk), prog)
        ec = e["ecart"]
        for h in horizons:
            t = debut + h - 1
            rows[(nom, h)] = ec.loc[t].to_dict()
    df = pd.DataFrame(rows).T
    df.index.names = ["régime", "horizon"]
    return df
