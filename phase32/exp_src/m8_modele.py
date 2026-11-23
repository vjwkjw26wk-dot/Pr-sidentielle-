"""M8 — Modèle macro-sectoriel dynamique annuel (version 0.1) : bouclage du bloc productif (M5), des équations de
comportement (lot 7), du revenu des ménages et des administrations publiques.

Pas annuel. Année de base B : un tableau entrées-sorties observé (2010-2022). Volumes aux prix de l'année de base
(pas de chaînage : acceptable sur un horizon de 5 à 10 ans, à revoir pour le long terme).

Enchaînement d'une année t (résolu par itérations de point fixe, amorties) :
 1. Prix : prix de la valeur ajoutée des 25 branches marchandes (équation de marge sur le coût salarial unitaire) ;
    branches non marchandes et immobilier : prix de la valeur ajoutée indexé sur le salaire moyen ; prix de production
    des 64 produits par le modèle de prix entrées-sorties (coûts intérieurs, prix d'importation par produit) ; prix des
    emplois finals (consommation, investissement, exportations, consommation publique).
 2. Salaire moyen par tête (courbe WS : prix à la consommation, productivité, part des salaires, chômage).
 3. Demande finale en volume : consommation (revenu disponible réel), consommation publique (exogène),
    investissement des 25 branches (accélérateur + coût d'usage du capital, dont l'impôt sur les sociétés), autres
    investissements (logement, administrations : exogènes), exportations (demande mondiale, compétitivité-prix).
 4. Importations : équation agrégée ; la répartition par produit garde la structure du tableau de base, avec un facteur
    commun d'ajustement des parts importées ; option de réindustrialisation : parts importées réduites par produit.
 5. Production par produit (Leontief), valeur ajoutée par branche, emploi par branche (équation de demande de travail),
    chômage (population active exogène, issue de M1 en projection).
 6. Revenus des ménages (masse salariale, revenus d'indépendants et du patrimoine, prestations, cotisations, impôts) et
    comptes des administrations publiques (recettes à taux apparents constants sauf mesure, dépenses, intérêts, dette).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np
EXP = {}
import pandas as pd

import m5_productif as m5
import m7_equations as E
import m7_series as S
from telechargement import jsonstat_dict, telecharger

RHO_DEFAUT = 0.2    # v0.8 (0,15 avant) : estimé avec θ (phase31/estimation_theta.py), plage 0,1-0,3 ; fermeture d'offre des projections (sensibilité : 0 et 1)
PART_K_ANTICIPATION = 1.0  # v0.8 : part du capital dans l'écart de potentiel anticipé (voir phase31/estimation_theta.py)
THETA_ANTICIPATION = 0.75 # v0.8 : estimé par la durée des écarts de production (phase31/estimation_theta.py), plage 0,5-1,0 ; v0.7 : 1,5 v0.7 : demande alignée sur les révisions du PIB potentiel (revenu permanent) ; 1,5 ferme l'écart des chocs d'offre en rampe (tests 1,0 / 1,5 / 2,0, phase3/test_fermeture.py) [H]
AMORTI_PRODUCTION = 0.0  # v0.8 (0,3 en v0.7, choix fondé sur un défaut de code) ; v0.7 : terme proportionnel de la fermeture sur l'écart de production (vérifié par simulation)
AMORTI_FERMETURE = 0.0   # v0.8 : identique au terme proportionnel de la fermeture sur l'écart de production (0,3 avant) ; terme proportionnel du correcteur, limite les dépassements (calibré par simulation)
OKUN = 1.5      # points de PIB par point de chômage (ordre de grandeur des estimations françaises de la loi d'Okun)
# ---- Version 0.7 (phase 3) : bloc d'offre et fermeture par l'écart de production -------------------------------------
# Production potentielle : ln Y*_t = ln A_t + α ln K_{t−1} + (1 − α) ln N*_t + Σ_{s≤t} π_s, avec N* = population active ×
# (1 − u*), K le capital des branches marchandes, π les chocs de productivité par tête (mesures, chocs d'environnement)
# et A la productivité globale des facteurs de la référence, déduite de la trajectoire de référence en posant que son écart
# de production est −OKUN × (u − u*) (loi d'Okun ; aucune donnée d'écart de production n'est importée).
ALPHA_K = 0.35          # part du capital dans la fonction de production (comptes nationaux : part de l'EBE ≈ 1/3) [C]
KAPPA_PRIX = 0.10       # hausse annuelle du prix de la VA des branches non industrielles par point d'écart de production
#                         de l'année précédente (pente de courbe de Phillips ; 0,05-0,2 dans la littérature) [L]
MU_IMPORT = 0.0         # élasticité des importations à la variation de l'écart de production (goulots, capacités) [L/H]
# ---- Version 0.7 : comportements (phase 3). Valeurs centrales ; plages et sources dans phase3/PARAMETRES (doc 15) ----
PSI_CHOMAGE = 0.3       # épargne de précaution : baisse de la consommation (%) par point de hausse du chômage [H/L]
PSI_TAUX = 0.2          # baisse de la consommation (%) par point de hausse du taux d'intérêt réel (l'année même) [L]
ASYM_SALAIRES = 0.5     # rigidité salariale à la baisse : effet du chômage sur les salaires réduit de moitié quand le
#                         chômage est au-dessus du structurel (rigidité nominale à la baisse documentée en France) [L]
SEMI_ELAST_IS, PART_IS_MULTINAT = 0.8, 0.5   # transfert de bénéfices : semi-élasticité de la base de l'IS au taux (0,2-1,5,
#                         Heckemeyer-Overesch 2017 ; Beer-de Mooij-Liu 2020), appliquée à la part de l'IS payée par les groupes [L]
THETA_TRESORERIE = 0.10 # part des profits conservés (mesures) réinvestie par les entreprises contraintes en trésorerie
#                         (évaluations du CICE et des réformes de la fiscalité des dividendes : effets non détectés) [L/H]
ELAST_DELOC_ENERGIE = 0.15  # élasticité des parts importées des produits énergo-intensifs au prix relatif de l'énergie
#                         importée (écart à 2025) ; OCDE : −0,7 % d'emploi manufacturier pour +10 % de prix [L/H]
ENERGO_INTENSIFS = ("CPA_C17", "CPA_C20", "CPA_C23", "CPA_C24")
DEPENSE_ARE_BASE = 0.015  # allocations chômage (≈ 40 Md€) en part du PIB nominal de l'année de base, proportionnelles au nombre de
#                         chômeurs (stabilisateur automatique ; absent de la v0.6 malgré la documentation) [A]
PRODUITS_NM = ["CPA_L68A", "CPA_L68B", "CPA_O", "CPA_P", "CPA_Q86", "CPA_Q87_88"]
# Importations non concurrentes (audit de novembre 2026) : houille, pétrole et gaz bruts, produits raffinés, électricité
# et gaz distribué. Leur part importée par produit ne s'ajuste pas au facteur commun φ, et leur prix est exclu du prix
# relatif de l'équation d'importations : une hausse du prix de l'énergie importée ne crée pas de substitution vers la
# production nationale d'autres produits (avant correction : +1 point de PIB fictif pour un choc de +50 %).
NON_CONCURRENTS = ("CPA_B", "CPA_C19", "CPA_D")
DELAI_CAPACITES = 2      # années entre la décision d'investir et la mise en service d'une capacité industrielle (hypothèse D,
#                          ordre de grandeur des projets industriels : 18 mois à 4 ans)
CAT = {"C": ["P3_S14"], "G": ["P3_S13", "P3_S15"], "I": ["P51G"], "S": ["P52", "P53"], "X": ["P6"]}


def _json(nom):
    return pd.Series(jsonstat_dict(json.loads((S.RACINE / "data" / "raw" / nom).read_text())))


def comptes_menages_apu():
    """Comptes des ménages (S14-S15) et des administrations publiques (S13), 1995-2025, M€ courants."""
    h = _json("eurostat_nasa_10_nf_tr_S14comp_FR.json")
    g = _json("eurostat_gov_10a_main_FR.json")
    dette = _json("eurostat_gov_10dd_edpt1_long_FR.json")
    an = range(1995, 2026)
    v = lambda s, *k: float(s.get(k, np.nan))  # noqa: E731
    men = pd.DataFrame({
        "d1": [v(h, "RECV", "D1", str(t)) - v(h, "PAID", "D1", str(t)) for t in an],
        "ebe": [v(h, "PAID", "B2A3G", str(t)) for t in an],
        "d4": [v(h, "RECV", "D4", str(t)) - v(h, "PAID", "D4", str(t)) for t in an],
        "d62": [v(h, "RECV", "D62", str(t)) - v(h, "PAID", "D62", str(t)) for t in an],
        "d7": [v(h, "RECV", "D7", str(t)) - v(h, "PAID", "D7", str(t)) for t in an],
        "d61": [v(h, "PAID", "D61", str(t)) - (v(h, "RECV", "D61", str(t)) if not np.isnan(v(h, "RECV", "D61", str(t))) else 0) for t in an],
        "d5": [v(h, "PAID", "D5", str(t)) for t in an],
        "rdb": [v(h, "PAID", "B6G", str(t)) for t in an]}, index=list(an))
    men["autres"] = men.rdb - (men.d1 + men.ebe + men.d4 + men.d62 + men.d7 - men.d61 - men.d5)
    apu = pd.DataFrame({k.lower(): [v(g, k, str(t)) for t in an] for k in
                        ["TR", "TE", "D2REC", "D5REC", "D61REC", "D62PAY", "P3", "D41PAY", "B9", "D1PAY", "P51G", "D632PAY"]}, index=list(an))
    apu["dette"] = [float(dette.get(str(t), np.nan)) for t in an]
    return men, apu


def emploi_total():
    pe = _json("eurostat_nama_10_pe_FR.json")
    an = range(1995, 2026)
    return pd.DataFrame({"emploi": [float(pe.get(("EMP_DC", str(t)), np.nan)) for t in an],
                         "salaries": [float(pe.get(("SAL_DC", str(t)), np.nan)) for t in an],
                         "population": [float(pe.get(("POP_NC", str(t)), np.nan)) for t in an]}, index=list(an))


@dataclass
class Exogenes:
    """Trajectoires exogènes (indices ou niveaux par année). Les valeurs absentes sont prolongées à l'identique."""
    demande_mondiale: pd.Series            # volume, indice
    prix_mondial: pd.Series                # prix des concurrents à l'exportation (indice)
    prix_import: pd.DataFrame              # indice de prix d'importation par produit (colonnes = produits A64)
    conso_publique: pd.Series              # volume, indice
    autres_investissements: pd.Series      # volume : FBCF des administrations, ISBLSM et branches non marchandes, hors ménages (v0.6)
    population_active: pd.Series           # milliers
    chomage_structurel: pd.Series          # %
    taux_long: pd.Series                   # %
    taux_is: pd.Series                     # %
    prestations_volume: pd.Series          # croissance en volume des prestations (hors chômage), indice
    duree_travail: pd.Series = None        # non utilisé en v0.1
    parts_importees: dict = field(default_factory=dict)   # réindustrialisation : {produit: facteur sur la part importée}
    parametres_alternatifs: dict = None    # analyse de sensibilité : {"debut", "params": {équation: Series}, "sigma", "phillips"}
    marges_branche: dict = None            # {branche: {année: log du supplément de prix de VA}} (contre-expertise : prix de marché
    #                                        de l'énergie produite en France, marges) ; persistant, sans rappel vers le coût
    reindustrialisation: dict = None       # {"produits": {produit: facteur final sur la part importée}, "debut": année,
    #                                        "duree": années de montée en charge, "surcout": surcoût relatif de la VA produite
    #                                        en France à la place des importations}
    mesure_menages: dict = None            # {"impots": ΔM€, "prestations": ΔM€} de la microsimulation (M10), indexés sur le PIB nominal
    fermeture_offre: float = 0.0           # ρ : part annuelle de l'écart de chômage résorbée (0 = modèle de demande pur)
    emploi_additionnel: pd.Series = None   # emplois (milliers) hors équations de branche : seniors maintenus en emploi (M9)
    ajust_prestations: pd.Series = None    # variation des prestations versées aux ménages (M€ courants), ex. pensions (M9)
    patrimoine_endogene: bool = False      # revenus du patrimoine des ménages par équations estimées (sinon ∝ PIB nominal)
    theta_import: float = None             # part des variations de prix d'importation répercutée l'année même (défaut : estimée)
    phi_impose: pd.Series = None           # facteur commun des parts importées imposé (repris d'un compte central)
    choc_salaire: pd.Series = None         # hausse exogène du salaire (log), par année
    taux_cotisations: pd.Series = None     # taux apparent de cotisations sociales (si mesure)
    autres_depenses_pib: pd.Series = None  # dépenses publiques hors consommation, prestations et intérêts, en part du PIB (mesures)
    productivite: pd.Series = None         # écart à la tendance de productivité par tête des branches (points de log par an)
    lpgf: pd.Series = None                 # v0.7 : log de la productivité globale des facteurs de la référence (bloc d'offre) ;
    #                                        None = fermeture sur l'écart de chômage (v0.6, utilisée pour caler la référence)
    fermeture_mode: str = "production"     # "production" (v0.7) ou "chomage" (v0.6)
    lpot_ref: pd.Series = None             # v0.7 : log du PIB potentiel de la référence (anticipation des chocs d'offre)
    lk_ref: pd.Series = None               # v0.7 : log du capital marchand de la référence (emploi de long terme)
    ly_ref: pd.Series = None               # v0.7 : log du PIB de la référence
    kappa_prix: float = None               # pente de Phillips sur les prix (défaut KAPPA_PRIX)
    mu_import: float = None                # effet des goulots sur les importations (défaut MU_IMPORT)
    comportements: dict = None             # v0.7 : surcharges des paramètres de comportement {"PSI_CHOMAGE": x, ...}
    ancrage: int = None                    # année d'ancrage : les termes de rappel (correction d'erreur) des équations sont
    #                                        mesurés par rapport à leur valeur de cette année (l'écart à l'équilibre estimé
    #                                        constaté alors est supposé durable) ; None = équilibre estimé
    niveaux: dict = None                   # mesures en niveau (voir _niv)
    calage: dict = None                    # termes de calage par année (compte de référence recalé sur l'observé) :
    #   "c", "x", "m", "investissement", "emploi", "prix", "salaire" : ajout au taux de croissance (log) de l'équation ;
    #   "recettes", "depenses" : ajout en points de PIB ; "dette" : ajustement stock-flux (M€)


def _par(ex, nom):
    """Paramètre de comportement v0.7 (surchargé par ex.comportements pour les analyses de sensibilité)."""
    c = getattr(ex, "comportements", None) or {}
    return c.get(nom, globals()[nom])


def _niv(ex, k, t) -> float:
    """Mesure en niveau (`Exogenes.niveaux[k]`, série par année ; 0 si absente) :
    "prix_conso" : écart (log) du prix de la consommation dû à une taxe (TVA, carbone) ;
    "impots_produits" : variation relative des impôts sur les produits ; "salaire_public" : variation relative de la
    rémunération par agent public (point d'indice)."""
    c = getattr(ex, "niveaux", None)
    if not c or k not in c:
        return 0.0
    return float(c[k].get(t, 0.0))


def _part_calage_emploi(ex, b, t) -> float:
    """Après l'année d'ancrage, le terme de calage de l'emploi (écart entre l'emploi du modèle et la cible de chômage)
    est porté par les branches hors industrie manufacturière, dont l'emploi a expliqué l'essentiel de l'écart
    2019-2025 ; l'emploi industriel suit ses propres équations."""
    a = getattr(ex, "ancrage", None)
    return 0.0 if (a is not None and t > a and b.startswith("C")) else 1.0


def _cal(ex, k, t) -> float:
    """Terme de calage de l'année t (0 si absent)."""
    c = getattr(ex, "calage", None)
    if not c or k not in c:
        return 0.0
    return float(c[k].get(t, 0.0))


class Modele:
    def __init__(self, base: int, fin_estimation: int | None = None):
        self.B = base
        fe = min(2019, base) if fin_estimation is None else fin_estimation
        self.tables = m5.charger_tables()
        self.T = m5.TableES(self.tables, base)
        self.P = list(self.T.actifs)
        self.panel = S.panel_branches()
        self.macro = S.macro()
        self.eq = E.toutes(self.panel, self.macro, E.DEBUT, fe)
        self.theta = float(self.eq["transmission"].lr["part transmise l'année même θ"])
        self.men, self.apu = comptes_menages_apu()
        self.eq["revenus_d4"] = E.revenus_menages(self.macro, self.men, "d4", E.DEBUT, fe)
        self.eq["revenus_ebe"] = E.revenus_menages(self.macro, self.men, "ebe", E.DEBUT, fe)
        self.men, self.apu = comptes_menages_apu()
        self.emp = emploi_total()
        self._preparer()

    # ---------------------------------------------------------------------------------------------------------------
    def _preparer(self):
        T, P = self.T, self.P
        n = len(P)
        self.x0 = T.x[P].to_numpy()
        self.Ad0 = T.Zd.loc[P, P].to_numpy() / self.x0
        self.Am0 = T.Zm.loc[P, P].to_numpy() / self.x0
        self.va0 = T.va.loc[P, "B1G"].to_numpy()
        self.tx0 = T.t[P].to_numpy()
        self.av = (self.va0) / self.x0                        # VA par unité produite
        self.at = self.tx0 / self.x0                          # impôts nets sur les produits (consommés) par unité
        self.Fd = {k: T.Fd.loc[P, c].sum(axis=1).to_numpy() for k, c in CAT.items()}
        self.Fm = {k: T.Fm.loc[P, c].sum(axis=1).to_numpy() for k, c in CAT.items()}
        self.tot = {k: self.Fd[k].sum() + self.Fm[k].sum() for k in CAT}
        self.struct = {k: (self.Fd[k] + self.Fm[k]) / self.tot[k] for k in CAT}
        self.part_imp = {k: np.divide(self.Fm[k], self.Fd[k] + self.Fm[k], out=np.zeros(n), where=(self.Fd[k] + self.Fm[k]) > 0) for k in CAT}
        Atot = self.Ad0 + self.Am0
        self.Atot = Atot
        self.part_imp_ci = np.divide(self.Am0, Atot, out=np.zeros_like(Atot), where=Atot > 0)
        self.concurrent = np.array([0.0 if p in NON_CONCURRENTS else 1.0 for p in self.P])
        imp0 = self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT)
        self.poids_pm_nc = imp0 * self.concurrent / (imp0 * self.concurrent).sum()   # pondération du prix des importations concurrentes
        # branche de chaque produit
        inv = {p: b for b, ps in S.VERS_A64.items() for p in ps}
        self.br_prod = np.array([inv.get(p, "NM") for p in P])
        self.BR = S.BRANCHES
        # historiques des branches
        pn = self.panel.set_index(["branche", "annee"])
        self.hist = {b: pn.loc[b] for b in self.BR}
        # parts de valeur ajoutée des produits dans chaque branche (pour l'emploi : q de branche = VA des produits)
        B = self.B
        self.q_obs_B = {b: self.hist[b].q[B] for b in self.BR}
        self.va_br0 = {b: self.va0[self.br_prod == b].sum() for b in self.BR + ["NM"]}
        em = self.emp
        self.n_nm0 = em.emploi[B] - sum(self.hist[b].n[B] for b in self.BR)
        self._caler()
        m = self.macro
        self.w0 = None

    # ---------------------------------------------------------------------------------------------------------------
    def _caler(self, nb_annees=5):
        """Constantes de branche recalées sur les résidus moyens des dernières années observées (hors 2020-2021), au lieu
        d'extrapoler les effets fixes et tendances estimés sur 1997-2019 (« calage des résidus »).
        Emploi : la tendance de productivité de chaque branche devient un paramètre explicite g_b (croissance moyenne de
        la productivité par tête sur les 8 dernières années observées hors 2020-2021), modifiable en scénario."""
        B = self.B
        ans = [t for t in range(B - 12, B + 1) if t not in (2020, 2021)][-nb_annees:]
        ans_g = [t for t in range(B - 10, B + 1) if t not in (2020, 2021, 2022)][-8:]
        re, rp, ri = (self.eq[k].res.params for k in ("emploi", "prix_va", "investissement"))
        self.c_emp, self.c_prix, self.c_inv, self.g_prod = {}, {}, {}, {}
        # taux d'utilisation des capacités (industrie manufacturière, enquête Insee) : niveau de base, moyenne de
        # référence 1995-2019 et croissance tendancielle de la capacité à capital donné (g_cap)
        TUC = S.tuc()
        self.tuc_moy = TUC.loc[1995:2019].mean()
        self.tuc_B, self.g_cap = {}, {}
        for b, grp in S.TUC_BRANCHE.items():
            h = self.hist[b]
            serie = TUC[grp]
            self.tuc_B[b] = float(serie[B])
            self.g_cap[b] = float(np.mean([np.log(h.q[t] / h.q[t - 1]) - np.log(h.k[t - 1] / h.k[t - 2]) - np.log(serie[t] / serie[t - 1])
                                           for t in ans_g]))
        tucd = lambda b, t: float(TUC.loc[t, S.TUC_BRANCHE[b]] - self.tuc_moy[S.TUC_BRANCHE[b]]) if b in S.TUC_BRANCHE else 0.0  # noqa: E731
        for b in self.BR:
            h = self.hist[b]
            ln, lq, lpva, li, lk = np.log(h.n), np.log(h.q), np.log(h.va_cp / h.q), np.log(h.i), np.log(h.k)
            lcn = np.log(h.wb / h.ns)
            lclu = lcn + ln - lq
            g = float(np.mean([(lq[t] - lq[t - 1]) - (ln[t] - ln[t - 1]) for t in ans_g]))
            self.g_prod[b] = g
            res_e, res_p, res_i = [], [], []
            for t in ans:
                z = ln[t - 1] - lq[t - 1] + E.SIGMA_TRAVAIL * (lcn[t - 1] - lpva[t - 1]) + g * (t - 1 - B)
                res_e.append((ln[t] - ln[t - 1]) - (re["dlq"] * (lq[t] - lq[t - 1]) + re["dlq_1"] * (lq[t - 1] - lq[t - 2])
                                                   + re["dlh_1"] * (ln[t - 1] - ln[t - 2]) + re["ecm_1"] * z))
                res_p.append((lpva[t] - lpva[t - 1]) - (rp["dlclu"] * (lclu[t] - lclu[t - 1]) + rp["dlq"] * (lq[t] - lq[t - 1])
                                                       + rp.get("tucd", 0.0) * tucd(b, t) + rp["ecm_1"] * (lpva[t - 1] - lclu[t - 1])))
                res_i.append((li[t] - li[t - 1]) - (ri["dlq"] * (lq[t] - lq[t - 1]) + ri["dlq_1"] * (lq[t - 1] - lq[t - 2])
                                                   + ri["li_1"] * li[t - 1] + ri["lk_1"] * lk[t - 1] + ri["lq_1"] * lq[t - 1]))
            self.c_emp[b], self.c_prix[b], self.c_inv[b] = map(lambda v: float(np.mean(v)), (res_e, res_p, res_i))

    def _ecart_initial(self, theta, recul=4):
        T, B = self.tables, self.B
        e = np.zeros(len(self.P))
        for t in range(B - recul + 1, B + 1):
            g = []
            for p in self.P:
                c = float(T["OFFRE"].get(("P7", p, str(t)), np.nan)); y = float(T["OFFRE_PYP"].get(("P7", p, str(t)), np.nan))
                g.append(np.log(c / y) if (c > 50 and y > 0) else np.log(self.macro.p_m[t] / self.macro.p_m[t - 1]))
            g = np.array(g)
            # e_t = ln pm_eff_t − ln pm_t ; pm_t = pm_{t−1} e^g ; pm_eff suit avec le coefficient θ
            e = (1 - theta) * (e - g)
        return e

    # ---------------------------------------------------------------------------------------------------------------
    def _leontief(self, phi, fact_imp):
        """Production et importations pour une demande finale par catégorie (volumes, prix de base)."""
        n = len(self.P)
        phi_p = 1.0 + (phi - 1.0) * self.concurrent            # φ ne s'applique qu'aux importations concurrentes
        pim = np.clip(self.part_imp_ci * phi_p[:, None] * fact_imp[:, None], 0, 1)
        Am = self.Atot * pim
        Ad = self.Atot - Am
        fd = np.zeros(n)
        fm = np.zeros(n)
        for k in CAT:
            v = self.struct[k] * self.dem[k]
            sh = np.clip(self.part_imp[k] * (phi_p if k != "X" else 1.0) * fact_imp, 0, 1)
            fd += v * (1 - sh)
            fm += v * sh
        x = np.linalg.solve(np.eye(n) - Ad, fd)
        m = Am @ x + fm
        return x, m.sum(), Ad, Am

    def _prix(self, pva_prod, pm):
        """p = (pm Am + pva av + p at... ) (I − Ad)⁻¹ ; impôts sur produits proportionnels au prix de production."""
        n = len(self.P)
        cout = pm @ self.Am0 + pva_prod * self.av
        return np.linalg.solve((np.eye(n) - self.Ad0 - np.diag(self.at)).T, cout)

    # ---------------------------------------------------------------------------------------------------------------
    def simuler(self, annees, ex: Exogenes, iterations=60, amorti=0.5, observe_jusqu_a=None):
        B, P, BR = self.B, self.P, self.BR
        r = {k: e.res.params for k, e in self.eq.items()}
        m, men, apu, em = self.macro, self.men, self.apu, self.emp
        H = {}
        self.H = H                                   # historiques (observés jusqu'à B, simulés ensuite)
        # --- initialisation à partir des observations
        for b in BR:
            h = self.hist[b]
            H[b] = {v: {t: float(h[v][t]) for t in range(B - 3, B + 1)} for v in ("q", "n", "pva", "i", "k")}
            H[b]["cn"] = {t: float(h.wb[t] / h.ns[t]) for t in range(B - 3, B + 1)}
        g = self.panel.groupby("annee")[["wb", "ns", "n", "va_cp", "q"]].sum(min_count=1)
        A = {"w": {t: g.wb[t] / g.ns[t] for t in range(B - 3, B + 1)},
             "pva_m": {t: g.va_cp[t] / g.q[t] for t in range(B - 3, B + 1)},
             "prod_m": {t: g.q[t] / g.n[t] for t in range(B - 3, B + 1)},
             "pc": {t: m.p_c[t] for t in range(B - 3, B + 1)},
             "C": {t: m.c[t] for t in range(B - 3, B + 1)},
             "rdb": {t: men.rdb[t] for t in range(B - 3, B + 1)},
             "rdbc": {t: men.rdb[t] for t in range(B - 3, B + 1)},
             "mcu": {t: 1.0 for t in range(B - 3, B + 1)},
             "X": {t: m.x[t] for t in range(B - 3, B + 1)}, "M": {t: m.m[t] for t in range(B - 3, B + 1)},
             "u": {t: m.chomage[t] for t in range(B - 3, B + 1)},
             "px": {t: m.p_x[t] for t in range(B - 3, B + 1)}, "pm_agg": {t: m.p_m[t] for t in range(B - 3, B + 1)},
             "pm_nc": {t: m.p_m[t] for t in range(B - 3, B + 1)},
             "ppib": {t: m.p_pib[t] for t in range(B - 3, B + 1)}, "pib": {t: m.pib[t] for t in range(B - 3, B + 1)},
             "emploi": {t: em.emploi[t] for t in range(B - 3, B + 1)}}
        A["ebe"] = {t: men.ebe[t] for t in range(B - 3, B + 1)}
        self.A_courant = A
        A["d4"] = {t: men.d4[t] for t in range(B - 3, B + 1)}
        # constantes recalées : résidu moyen des 3 dernières années observées (hors 2020-2021)
        self.c_rev = {}
        for poste in ("ebe", "d4"):
            rr = self.eq["revenus_" + poste].res.params
            y, pn = np.log(men[poste]), np.log(m.pib_cp)
            res_ = [(y[t] - y[t - 1]) - (rr["const"] + rr["dpibn"] * (pn[t] - pn[t - 1]) + rr["dpc"] * np.log(m.p_c[t] / m.p_c[t - 1])
                                         + rr["ecm_1"] * (y[t - 1] - pn[t - 1]) + rr["r_1"] * m.taux_long[t - 1])
                    for t in [a for a in range(B - 6, B + 1) if a not in (2020, 2021)][-3:]]
            self.c_rev[poste] = float(np.mean(res_))
        D_ = E.demande_ponderee(m)
        A["D"] = {t: D_[t] for t in range(B - 3, B + 1)}
        # comptes en niveau à l'année de base
        mb, ab = men.loc[B], apu.loc[B]
        pib_n0 = m.pib_cp[B]
        cout_usage0 = None
        # demande finale de base (M€ prix de base de l'année B)
        dem0 = dict(self.tot)
        x_B, M_B, _, _ = self._leontief_base(dem0)
        res = []
        pva_prev = {b: 1.0 for b in BR}
        etat = {"C": dem0["C"], "I_br": {b: H[b]["i"][B] for b in BR}, "X": dem0["X"], "phi": 1.0,
                "w": 1.0, "pva": {b: 1.0 for b in BR}, "n": {b: H[b]["n"][B] for b in BR}}
        idx = {"pva": {b: 1.0 for b in BR}, "w": 1.0, "pc": 1.0, "px": 1.0, "pi": 1.0, "pg": 1.0, "ppib": 1.0}
        niv = {"x": x_B, "rdb": mb.rdb, "dette": ab.dette, "d62": mb.d62, "n_nm": self.n_nm0}
        hist_idx = {B: dict(idx)}
        hist_vol = {B: {"C": dem0["C"], "X": dem0["X"], "I": dem0["I"], "G": dem0["G"], "M": M_B, "q": {b: H[b]["q"][B] for b in BR},
                        "q_nm": self.va_br0["NM"], "n_nm": self.n_nm0, "u": m.chomage[B]}}
        I_autres0 = dem0["I"] - sum(H[b]["i"][B] * (self.T.Fd.loc[self.P, "P51G"].sum() + self.T.Fm.loc[self.P, "P51G"].sum()) / m.fbcf_cp[B] * 0 for b in BR)
        # part de la FBCF des branches marchandes dans la FBCF totale (base) : FBCF des branches en volume chaîné → base
        fbcf_br_B = sum(self.hist[b].i_cp[B] for b in BR)
        conv_I = dem0["I"] / m.fbcf_cp[B]                    # passage comptes nationaux → tableau (prix de base)
        I_autres_B = dem0["I"] - fbcf_br_B * conv_I
        # investissement des ménages (logement, M14 / audit 2026) : endogène, équation du lot 7 sur le revenu disponible
        dl = self.eq["logement"].data
        I_men_B = float(dl.i_cp[B]) * conv_I                      # part ménages de la FBCF « autres » (prix de base)
        A["Imen"] = {t: float(np.exp(dl.iv[t])) for t in range(B - 3, B + 1)}
        rl = r["logement"]
        res_l = [(dl.iv[a] - dl.iv[a - 1]) - (rl["const"] + rl["dlrdb"] * (dl.rdbr[a] - dl.rdbr[a - 1]) + rl["ecart_1"] * (dl.iv[a - 1] - dl.rdbr[a - 1]))
                 for a in [x for x in range(B - 6, B + 1) if x not in (2020, 2021)][-3:]]
        c_log = float(np.mean(res_l))
        fact_imp = np.array([ex.parts_importees.get(p, 1.0) for p in P])
        R = ex.reindustrialisation
        imp_prod0 = self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT)          # importations par produit, base
        kappa = np.array([(self.hist[b].k[B] / self.hist[b].q[B]) if b in self.hist else 0.0 for b in self.br_prod])
        delta_k = np.array([(1 - (self.hist[b].k[B] - self.hist[b].i[B]) / self.hist[b].k[B - 1]) if b in self.hist else 0.0 for b in self.br_prod])
        va_cap_prec = np.zeros(len(P))
        # Ajustement partiel des prix d'importation répercutés (θ estimé, lot 7) : ln pm_eff_t = ln pm_eff_{t−1} + θ (ln pm_t − ln pm_eff_{t−1}).
        # L'écart initial e_B = ln pm_eff_B − ln pm_B (hausses pas encore répercutées à l'année de base) est reconstitué
        # à partir des prix d'importation observés des 4 années précédant la base.
        theta = self.theta if ex.theta_import is None else ex.theta_import
        e_B = self._ecart_initial(theta)
        lpm_eff = {B: e_B}
        self._ecm_ref, self._ecm_B = {}, {}
        def ecm(cle, val):
            """Terme de rappel ; avec ancrage a : à partir de a + 1, l'écart à l'équilibre constaté en fin d'année a
            (relativement à celui de l'année de base, supposée à l'équilibre) est traité comme durable."""
            a = ex.ancrage
            if a is None:
                return val
            if t == B + 1:
                self._ecm_B[cle] = val
            if t == a + 1:
                self._ecm_ref[cle] = val - self._ecm_B.get(cle, val)
            if t >= a + 1:
                return val - self._ecm_ref.get(cle, 0.0)
            return val
        alt = ex.parametres_alternatifs or {}
        sauv_glob = (E.SIGMA_TRAVAIL, E.PHILLIPS)
        # v0.7 : écart de production (log), initialisé par la loi d'Okun sur le chômage observé
        u_star = lambda a: float(ex.chomage_structurel.get(a, ex.chomage_structurel.iloc[-1] if a > ex.chomage_structurel.index[-1] else ex.chomage_structurel.iloc[0]))  # noqa: E731
        gap_hist = {a: -OKUN * (float(m.chomage[a]) - u_star(a)) / 100 for a in (B - 1, B)}
        self.gap_hist = gap_hist
        dpot_hist = {}    # écart du log du PIB potentiel à celui de la référence (chocs d'offre cumulés)
        kappa_p = KAPPA_PRIX if ex.kappa_prix is None else ex.kappa_prix   # (nom distinct du ratio capital/production `kappa`)
        mu_imp = MU_IMPORT if ex.mu_import is None else ex.mu_import
        cum_prod = 0.0
        idx_en = np.array([P.index(p_) for p_ in NON_CONCURRENTS if p_ in P])
        idx_ei = np.array([P.index(p_) for p_ in ENERGO_INTENSIFS if p_ in P])
        erel_hist = getattr(self, "_erel_obs", {})
        erel_hist = dict(erel_hist)
        r_central = r
        theta_c = theta
        for t in annees:
            # paramètres alternatifs (analyse de sensibilité, v0.6) : appliqués à partir de alt["debut"] (2026 par défaut,
            # première année projetée) ; la période observée reste reproduite avec les paramètres centraux et l'ancrage
            # des termes de rappel absorbe les changements de niveau d'équilibre (sinon : dérive artificielle dès 2023).
            if alt and t >= alt.get("debut", 2026):
                r = {k: alt.get("params", {}).get(k, v) for k, v in r_central.items()}
                E.SIGMA_TRAVAIL = alt.get("sigma", sauv_glob[0])
                E.PHILLIPS = alt.get("phillips", sauv_glob[1])
                theta = alt.get("theta", theta_c)
            else:
                r = r_central
                E.SIGMA_TRAVAIL, E.PHILLIPS = sauv_glob
                theta = theta_c
            # valeurs initiales de l'itération : celles de l'année précédente
            prev = hist_vol[t - 1]
            C, X, phi = prev["C"], prev["X"], etat["phi"]
            I_br = {b: H[b]["i"][t - 1] for b in BR}
            q_br = dict(prev["q"])
            n_br = {b: H[b]["n"][t - 1] for b in BR}
            w = A["w"][t - 1]
            pva = {b: H[b]["pva"][t - 1] for b in BR}
            # réindustrialisation : montée en charge progressive, investissement de capacité, surcoût de production
            I_cap, surcout_prod, I_cap_br = 0.0, np.ones(len(P)), {}
            # fermeture d'offre (option) : une part ρ de l'écart de chômage au chômage structurel de l'année précédente
            # est résorbée chaque année par un supplément de demande intérieure (canaux non modélisés : politique
            # monétaire, conditions de crédit, confiance, compétitivité de moyen terme) ; terme intégral (persistant).
            rho = ex.fermeture_offre or 0.0
            if alt and t >= alt.get("debut", 2026) and "rho" in alt:
                rho = alt["rho"]
            z_ff = 0.0
            if rho and ex.lpgf is not None and ex.fermeture_mode == "production":
                # v0.7 : fermeture sur l'écart de production (Y − Y*) ; un choc d'offre (productivité, population active,
                # capital, chômage structurel) déplace Y* et la demande s'ajuste vers le nouveau potentiel. Dans la
                # référence, l'écart vaut −OKUN (u − u*) par construction : les deux fermetures y sont identiques.
                # années de base (≤ B) : même convention que l'ancienne fermeture, pour que la référence calée reste identique
                def _gf(a):
                    if a > B:
                        return gap_hist[a]
                    cs = ex.chomage_structurel
                    return -OKUN * (hist_vol[a]["u"] - float(cs.get(a, cs.iloc[-1]))) / 100
                g1 = _gf(t - 1)
                g2 = _gf(t - 2) if (t - 2) in hist_vol else g1
                # v0.8 : nom distinct de l'argument `amorti` de simuler (amortissement du point fixe) ; en v0.7, ce
                # paramètre écrasait l'amortissement du point fixe (0,5 → 0,3) : défaut corrigé
                a_ferm = _par(ex, "AMORTI_PRODUCTION")
                if alt and t >= alt.get("debut", 2026) and "amorti" in alt:   # v0.8 : variantes à partir d'une date
                    a_ferm = alt["amorti"]
                niv["Z"] = niv.get("Z", 0.0) - (rho * g1 + a_ferm * (g1 - g2))
                # anticipation : ménages et entreprises révisent leur revenu permanent quand le potentiel s'écarte de la
                # référence (part THETA_ANTICIPATION de l'écart de potentiel de l'année précédente, en demande)
                th_ = alt["theta"] if (alt and t >= alt.get("debut", 2026) and "theta" in alt) else _par(ex, "THETA_ANTICIPATION")
                z_ff = th_ * dpot_hist.get(t - 1, 0.0)
            elif rho:
                u_s = float(ex.chomage_structurel.get(t - 1, ex.chomage_structurel.iloc[-1]))
                g1 = hist_vol[t - 1]["u"] - u_s
                g2 = hist_vol[t - 2]["u"] - float(ex.chomage_structurel.get(t - 2, u_s)) if (t - 2) in hist_vol else g1
                # correcteur proportionnel-intégral (forme incrémentale) : ρ sur l'écart, AMORTI sur sa variation
                niv["Z"] = niv.get("Z", 0.0) + (rho * g1 + _par(ex, "AMORTI_FERMETURE") * (g1 - g2)) * OKUN / 100
            if alt.get("impulsion_Z"):   # diagnostic (réponse indicielle de la fermeture), sans effet par défaut
                niv["Z"] = niv.get("Z", 0.0) + float(alt["impulsion_Z"].get(t, 0.0))
            Z_dem = (niv.get("Z", 0.0) + z_ff) * (sum(self.va0) + sum(self.tx0))
            if R:
                # délai de construction (audit 2026) : les capacités sont financées et construites pendant `delai` ans
                # (2 ans par défaut) avant de produire ; la substitution aux importations suit les capacités en service.
                L_ = int(R.get("delai", DELAI_CAPACITES))
                prog_f = lambda a: min(1.0, max(0.0, (a - R["debut"] + 1 - L_) / R.get("duree", 5)))  # noqa: E731
                prog = prog_f(t)
                fact_imp = np.array([1 - (1 - R["produits"].get(p, 1.0)) * prog for p in P])
                croiss_m = hist_vol[t - 1]["M"] / M_B
                va_cap = (1 - fact_imp) * imp_prod0 * croiss_m * self.av      # VA des capacités en service (prix de base)
                # capacités en construction : investissement réparti sur le délai, en avance sur la production
                va_fut = (1 - np.array([1 - (1 - R["produits"].get(p, 1.0)) * prog_f(t + L_) for p in P])) * imp_prod0 * croiss_m * self.av
                va_fut_prec = (1 - np.array([1 - (1 - R["produits"].get(p, 1.0)) * prog_f(t - 1 + L_) for p in P])) * imp_prod0 * croiss_m * self.av
                I_cap_prod = kappa * np.maximum(va_fut - va_fut_prec, 0) + delta_k * kappa * va_cap_prec
                I_cap = float(I_cap_prod.sum())
                I_cap_br = {b: float(I_cap_prod[self.br_prod == b].sum()) for b in BR}
                surcout_prod = 1 + R.get("surcout", 0.0) * np.divide(va_cap, self.va0, out=np.zeros(len(P)), where=self.va0 > 0)
                va_cap_t = va_cap
            for it in range(iterations):
                # ---- 1. prix
                pm_brut = np.array([float(ex.prix_import.loc[t, p]) if p in ex.prix_import.columns else 1.0 for p in P])
                lpm_eff[t] = lpm_eff[t - 1] + theta * (np.log(pm_brut) - lpm_eff[t - 1])
                pm = np.exp(lpm_eff[t] - e_B)
                # v0.7 : délocalisation des productions énergo-intensives quand l'énergie importée renchérit (prix relatif,
                # écart à 2025 ; nul dans la référence où tous les prix d'importation suivent l'inflation de la zone euro)
                e_rel = float(pm[idx_en].mean() / (pm * self.poids_pm_nc).sum() * self.poids_pm_nc.sum())
                erel_hist[t] = e_rel
                fact_eff = fact_imp.copy()
                if t > 2025 and 2025 in erel_hist and _par(ex, "ELAST_DELOC_ENERGIE"):
                    fact_eff[idx_ei] = fact_eff[idx_ei] * (e_rel / erel_hist[2025]) ** _par(ex, "ELAST_DELOC_ENERGIE")
                w_idx = w / A["w"][B]
                pva_prod = np.array([pva[b] / H[b]["pva"][B] if b in pva else w_idx for b in self.br_prod]) * surcout_prod
                pp = self._prix(pva_prod, pm)
                def pfin(k):
                    v = self.struct[k] * self.tot[k]
                    sh = self.part_imp[k] * phi
                    return float(((v * (1 - sh) * pp).sum() + (v * sh * pm).sum()) / v.sum())
                pc_idx, px_idx, pi_idx = pfin("C"), pfin("X"), pfin("I")
                pc = m.p_c[B] * pc_idx * float(np.exp(_niv(ex, "prix_conso", t)))
                px = m.p_x[B] * px_idx
                pm_agg = m.p_m[B] * float((pm * (self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT))).sum() / (self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT)).sum())
                pm_nc = m.p_m[B] * float((pm * self.poids_pm_nc).sum())
                # ---- 2. salaires (secteur marchand, par tête)
                qm = sum(q_br.values()); nm = sum(n_br.values())
                prod_m = qm / nm
                vam = sum(q_br[b] * pva[b] for b in BR)
                pva_m = vam / qm
                u_prev = hist_vol[t - 1]["u"]
                rw = r["salaires"]
                ugap = u_prev - float(ex.chomage_structurel.get(t, ex.chomage_structurel.iloc[-1]))
                dlw = (rw["const"] + rw["dlpc"] * np.log(pc / A["pc"][t - 1]) + rw["dlprod"] * np.log(prod_m / A["prod_m"][t - 1])
                       + rw["ecm_1"] * (np.log(A["w"][t - 1]) - np.log(A["pva_m"][t - 1]) - np.log(A["prod_m"][t - 1]))
                       + E.PHILLIPS * ugap * (_par(ex, "ASYM_SALAIRES") if ugap > 0 else 1.0))
                dlw = dlw - rw["ecm_1"] * (np.log(A["w"][t - 1]) - np.log(A["pva_m"][t - 1]) - np.log(A["prod_m"][t - 1])) \
                    + ecm("w", rw["ecm_1"] * (np.log(A["w"][t - 1]) - np.log(A["pva_m"][t - 1]) - np.log(A["prod_m"][t - 1])
                                              - _niv(ex, "ancre_salaire", t)))
                # v0.8 : "ancre_salaire" (log) déplace la cible de long terme du coût salarial par tête : incidence de long
                # terme des prélèvements sur les entreprises (part supportée par les salariés), document 19
                if ex.choc_salaire is not None:
                    dlw += float(ex.choc_salaire.get(t, 0.0))
                dlw += _cal(ex, "salaire", t)
                w_new = A["w"][t - 1] * np.exp(dlw)
                # ---- 3. prix de la valeur ajoutée et emploi par branche
                re, rp, ri = r["emploi"], r["prix_va"], r["investissement"]
                pva_new, n_new, I_new = {}, {}, {}
                m_cu1 = A["mcu"].get(t - 1, 1.0)     # multiplicateur du coût d'usage appliqué l'année précédente
                # v0.7 : approfondissement du capital (cohérence avec le PIB potentiel Cobb-Douglas). Quand le capital croît
                # plus vite que la production par rapport à la référence, la cible d'emploi de long terme baisse de
                # α/(1−α) × (dk − dq) ; nul dans la référence.
                if ex.lk_ref is not None and t in ex.lk_ref.index and (t - 1) in ex.ly_ref.index and (t - 1) in A["pib"]:
                    # lk_ref[t] = capital de fin d'année t − 1 (colonne capital_marchand de l'année t)
                    dkq = (np.log(sum(H[b_]["k"][t - 1] for b_ in BR)) - float(ex.lk_ref[t])) - (np.log(A["pib"][t - 1]) - float(ex.ly_ref[t - 1]))
                    cible_k = _par(ex, "ALPHA_K") / (1 - _par(ex, "ALPHA_K")) * dkq
                else:
                    cible_k = 0.0
                for b in BR:
                    hb = H[b]
                    cn = hb["cn"][B] * w_new / A["w"][B]
                    cn_1 = hb["cn"][t - 1]
                    eff = lambda rr: rr.get("const", 0) + rr.get(f"fe_{b}", 0) + rr.get(f"tr_{b}", 0) * (t - 2010)  # noqa: E731
                    lq, lq1, lq2 = np.log(q_br[b]), np.log(hb["q"][t - 1]), np.log(hb["q"][t - 2])
                    # emploi
                    lrc1 = np.log(cn_1) - np.log(hb["pva"][t - 1])
                    g_b = self.g_prod[b] + (0.0 if ex.productivite is None else float(ex.productivite.get(t, 0.0)))
                    dn = (self.c_emp[b] + re["dlq"] * (lq - lq1) + re["dlq_1"] * (lq1 - lq2) + re["dlh_1"] * (np.log(hb["n"][t - 1]) - np.log(hb["n"][t - 2]))
                          + ecm(("n", b), re["ecm_1"] * (np.log(hb["n"][t - 1]) - lq1 + E.SIGMA_TRAVAIL * lrc1 + self.g_prod[b] * (t - 1 - B) + cum_prod + cible_k))  # v0.7 : choc de productivité cumulé dans la cible de long terme (auparavant effacé par la correction d'erreur)
                          - (g_b - self.g_prod[b]) + _cal(ex, "emploi", t) * _part_calage_emploi(ex, b, t))
                    n_new[b] = hb["n"][t - 1] * np.exp(dn)
                    # prix de la VA
                    clu = cn * n_new[b] / q_br[b]
                    clu1 = cn_1 * hb["n"][t - 1] / hb["q"][t - 1]
                    tucd_b = self._tuc(b, t, q_br[b], H) - self.tuc_moy[S.TUC_BRANCHE[b]] if b in S.TUC_BRANCHE else 0.0
                    mk = (ex.marges_branche or {}).get(b, {})
                    mk_t, mk_1 = float(mk.get(t, 0.0)), float(mk.get(t - 1, 0.0))
                    dp = (self.c_prix[b] + rp["dlclu"] * np.log(clu / clu1) + rp["dlq"] * (lq - lq1) + rp.get("tucd", 0.0) * tucd_b
                          + ecm(("p", b), rp["ecm_1"] * (np.log(hb["pva"][t - 1]) - np.log(clu1) - mk_1)) + _cal(ex, "prix", t)
                          + mk_t - mk_1 + (0.0 if b in S.TUC_BRANCHE else kappa_p * gap_hist[t - 1]))
                    pva_new[b] = hb["pva"][t - 1] * np.exp(dp)
                    # investissement (accélérateur) + coût d'usage
                    di = (self.c_inv[b] + ri["dlq"] * (lq - lq1) + ri["dlq_1"] * (lq1 - lq2)
                          + ri["li_1"] * np.log(hb["i"][t - 1] / m_cu1) + ri["lk_1"] * np.log(hb["k"][t - 1]) + ri["lq_1"] * lq1
                          + _cal(ex, "investissement", t))
                    # v0.6 : la dynamique de branche porte sur l'investissement hors effet du coût d'usage ; l'effet du coût
                    # d'usage est appliqué en niveau (en v0.5 il était réappliqué chaque année et se cumulait : effet de long
                    # terme d'une baisse d'IS environ 3,5 fois l'élasticité estimée)
                    I_new[b] = hb["i"][t - 1] / m_cu1 * np.exp(di)
                # effet du coût d'usage (IS, taux) : élasticité de long terme agrégée, ajustement à la vitesse des branches
                tau = float(ex.taux_is.get(t, ex.taux_is.iloc[-1])); tau0 = float(ex.taux_is.get(B, tau))
                rr_ = float(ex.taux_long.get(t, ex.taux_long.iloc[-1])); rr0 = float(ex.taux_long.get(B, rr_))
                lcu = np.log((max(rr_, -5) / 100 + E.DELTA_USAGE) / (1 - tau / 100)) - np.log((max(rr0, -5) / 100 + E.DELTA_USAGE) / (1 - tau0 / 100))
                eps_cu = self.eq["investissement_snf"].lr["long terme : élasticité au coût d'usage du capital"]
                if alt and t >= alt.get("debut", 2026) and "investissement_snf" in alt.get("params", {}):
                    pa = alt["params"]["investissement_snf"]
                    eps_cu = -float(pa["lcu_1"]) / float(pa["ecm_1"])
                # convergence progressive vers l'effet de long terme ε·Δln(coût d'usage), à la vitesse de rappel des branches
                # (v0.6 ; en v0.5 la vitesse était comptée depuis l'année de base, d'où un effet presque immédiat en 2028)
                m_cu = float(np.exp(np.log(m_cu1) + (-ri["li_1"]) * (eps_cu * lcu - np.log(m_cu1))))
                I_new = {b: v * m_cu for b, v in I_new.items()}
                # PIB nominal (indice, base B) : VA marchande en valeur + VA non marchande (volume × salaire)
                q_nm_c = hist_vol[t - 1]["q_nm"] if it == 0 else q_nm
                vm = sum(q_br[b] / H[b]["q"][B] * self.hist[b].va_cp[B] * pva_new[b] / H[b]["pva"][B] for b in BR)
                vm0 = sum(self.hist[b].va_cp[B] for b in BR)
                s_m = sum(self.va_br0[b] for b in BR) / sum(self.va_br0.values())
                idx_nom = s_m * vm / vm0 + (1 - s_m) * (q_nm_c / self.va_br0["NM"]) * (w_new / A["w"][B]) * (EXP["wpub"](t) if "wpub" in EXP else 1.0)
                vol_m = sum(q_br[b] for b in BR) / sum(H[b]["q"][B] for b in BR)
                idx_vol = s_m * vol_m + (1 - s_m) * q_nm_c / self.va_br0["NM"]
                A["pib_nom_idx"] = A.get("pib_nom_idx", {B: 1.0})
                idx_nom *= float(np.exp(_cal(ex, "pib_nominal", t)))
                A["pib_nom_idx"][t] = idx_nom
                ppib_est = m.p_pib[B] * idx_nom / idx_vol
                # ---- 4. demande finale
                rc = r["consommation"]
                rdb = self._rdb(t, w_new, n_new, niv, hist_vol, A, ex, pc, mb)
                rdb_c = rdb + self._conso_effectif(ex, t)          # hétérogénéité des propensions (M14)
                rdbr, rdbr1 = rdb_c / pc, A["rdbc"][t - 1] / A["pc"][t - 1]
                u_cur = prev["u"] if it == 0 else u_cur
                # v0.7 : épargne de précaution (variation du chômage) et taux d'intérêt réel (variation)
                rr_t = float(ex.taux_long.get(t, ex.taux_long.iloc[-1])) - 100 * np.log(A["pc"][t - 1] / A["pc"][t - 2]) if (t - 2) in A["pc"] else 0.0
                rr_1 = float(ex.taux_long.get(t - 1, ex.taux_long.iloc[0])) - 100 * np.log(A["pc"][t - 2] / A["pc"][t - 3]) if (t - 3) in A["pc"] else rr_t
                dC = (rc["const"] + rc["dlrdb"] * np.log(rdbr / rdbr1) + rc.get("du", 0.0) * (u_cur - prev["u"]) + ecm("c", rc["ecart_1"] * (np.log(A["C"][t - 1]) - np.log(rdbr1))) + _cal(ex, "c", t)
                      - _par(ex, "PSI_CHOMAGE") / 100 * (u_cur - prev["u"]) - _par(ex, "PSI_TAUX") / 100 * (rr_t - rr_1))
                C_cn = A["C"][t - 1] * np.exp(dC)
                rx = r["exportations"]
                pw = float(ex.prix_mondial[t]) / float(ex.prix_mondial[t - 1])
                dX = rx["const"] + rx["dldm"] * np.log(float(ex.demande_mondiale[t]) / float(ex.demande_mondiale[t - 1])) + rx["dlprel"] * (np.log(px / A["px"][t - 1]) - np.log(pw)) + _cal(ex, "x", t)
                X_cn = A["X"][t - 1] * np.exp(dX)
                G_idx = float(ex.conso_publique[t]) / float(ex.conso_publique[B])
                fbcf_br = sum(I_new[b] / self.hist[b].i[B] * self.hist[b].i_cp[B] for b in BR) * conv_I
                dIm = (rl["const"] + c_log + rl["dlrdb"] * np.log(rdbr / rdbr1)
                       + ecm("log", rl["ecart_1"] * (np.log(A["Imen"][t - 1]) - np.log(rdbr1))) + _cal(ex, "logement", t))
                Imen = A["Imen"][t - 1] * np.exp(dIm)
                # FBCF « autres » (APU, ISBLSM, ménages) : l'indice exogène s'applique au total de l'année de base, de sorte que
                # les mesures (investissement public, logements sociaux) gardent leur montant ; la part des ménages est
                # remplacée par sa valeur endogène.
                # v0.6 (contre-expertise) : `autres_investissements` exclut désormais l'investissement des ménages (endogène).
                # En v0.5, l'indice observé incluait le logement des ménages, compté une seconde fois par l'équation de
                # logement dans les rétrosimulations (double compte de la dynamique du logement).
                I_tot = (fbcf_br + (I_autres_B - I_men_B) * float(ex.autres_investissements[t]) / float(ex.autres_investissements[B])
                         + I_men_B * Imen / A["Imen"][B] + I_cap
                         + _par(ex, "THETA_TRESORERIE") * self._profits(ex, t)["conserve"] / pi_idx)
                self.dem = {"C": dem0["C"] * C_cn / m.c[B] + 0.6 * Z_dem, "G": dem0["G"] * G_idx, "I": I_tot + 0.4 * Z_dem, "S": dem0["S"] + _cal(ex, "stocks", t) * sum(self.va0),
                            "X": dem0["X"] * X_cn / m.x[B]}
                # ---- 5. importations (équation agrégée) et production
                rm = r["importations"]
                D = sum(w_ * v for w_, v in zip(E.CONTENU_IMPORT.values(), (self.dem["C"] / dem0["C"] * m.c[B], self.dem["G"] / dem0["G"] * m.g[B],
                                                                            (self.dem["I"] + self.dem["S"]) / (dem0["I"] + dem0["S"]) * m.fbc[B], X_cn)))
                lprel, lprel1 = np.log(pm_nc / ppib_est), np.log(A["pm_nc"][t - 1] / A["ppib"][t - 1])
                dM = (rm["const"] + rm["dld"] * np.log(D / A["D"][t - 1]) + rm["dlprel"] * (lprel - lprel1)
                      + ecm("m", rm["lm_1"] * np.log(A["M"][t - 1]) + rm["ld_1"] * np.log(A["D"][t - 1]) + rm["lprel_1"] * lprel1)
                      + rm["t"] * (t - 2010) + _cal(ex, "m", t) + mu_imp * (gap_hist[t - 1] - gap_hist.get(t - 2, gap_hist[t - 1])))
                M_cn = A["M"][t - 1] * np.exp(dM)
                M_cible = M_B * M_cn / m.m[B]
                lo, hi = 0.3, 3.0
                for _ in range(40):
                    phi_ = 0.5 * (lo + hi)
                    x, Mtot, Ad, Am = self._leontief(phi_, fact_eff)
                    if Mtot > M_cible:
                        hi = phi_
                    else:
                        lo = phi_
                if ex.phi_impose is not None:
                    # variante de réindustrialisation : comportement d'importation des autres produits inchangé (facteur
                    # commun repris du compte central), parts importées des produits ciblés réduites
                    phi_ = float(ex.phi_impose[t])
                    x, Mtot, Ad, Am = self._leontief(phi_, fact_eff)
                    M_cn = m.m[B] * Mtot / M_B
                va_prod = self.av * x
                q_new = {b: H[b]["q"][B] * va_prod[self.br_prod == b].sum() / self.va_br0[b] for b in BR}
                q_nm = va_prod[self.br_prod == "NM"].sum()
                n_nm = self.n_nm0 * q_nm / self.va_br0["NM"]
                n_nm = EXP["n_nm"](self, t, q_nm, n_nm) if "n_nm" in EXP else n_nm
                niv["n_nm"] = n_nm
                emploi = sum(n_new.values()) + n_nm + self._extra(ex, "emploi_additionnel", t)
                u_new = 100 * (1 - emploi / float(ex.population_active[t]))
                # ---- amortissement et convergence
                ecart = abs(np.log(sum(q_new.values()) / sum(q_br.values()))) + abs(np.log(w_new / w)) + abs(u_new - u_cur) / 100
                q_br = {b: q_br[b] ** (1 - amorti) * q_new[b] ** amorti for b in BR}
                n_br, pva, w, phi, u_cur = n_new, pva_new, w_new, phi_, u_new
                if ecart < 1e-7 and it > 2:
                    break
            if R:
                va_cap_prec = va_cap_t
            # ---- enregistrement de l'année t
            for b in BR:
                hb = H[b]
                hb["q"][t], hb["n"][t], hb["pva"][t], hb["i"][t] = q_br[b], n_br[b], pva[b], I_new[b]
                hb["cn"][t] = hb["cn"][B] * w / A["w"][B]
                delta = 1 - (self.hist[b].k[B] - self.hist[b].i[B]) / self.hist[b].k[B - 1]
                # capital : investissement de la branche + investissement de capacité (réindustrialisation), converti
                # des prix de base du tableau en volume des comptes de branche au prorata de la FBCF de base
                i_cap_vol = I_cap_br.get(b, 0.0) * self.hist[b].i[B] / max(self.hist[b].i_cp[B] * conv_I, 1e-9)
                hb["k"][t] = hb["k"][t - 1] * (1 - delta) + I_new[b] + i_cap_vol
            A["w"][t], A["pva_m"][t], A["prod_m"][t], A["pc"][t] = w, pva_m, prod_m, pc
            A["C"][t], A["rdb"][t], A["X"][t], A["M"][t], A["u"][t] = C_cn, rdb, X_cn, M_cn, u_cur
            A["rdbc"][t] = rdb_c
            A["mcu"][t] = m_cu
            A["Imen"][t] = Imen
            A["px"][t], A["pm_agg"][t], A["D"][t], A["ppib"][t] = px, pm_agg, D, ppib_est
            A["pm_nc"][t] = pm_nc
            A["ebe"][t], A["d4"][t] = self._revenus_patrimoine(t, A, ex, pc)
            pib_vol = (sum(q_br.values()) / sum(H[b]["q"][B] for b in BR) * sum(self.va_br0[b] for b in BR) + q_nm) / sum(self.va_br0.values())
            A["pib"][t] = m.pib[B] * pib_vol
            A["emploi"][t] = emploi
            # ---- v0.7 : production potentielle et écart de production de l'année t
            k_agg = sum(H[b]["k"][t - 1] for b in BR)
            n_star = float(ex.population_active[t]) * (1 - u_star(t) / 100)
            cum_prod += 0.0 if ex.productivite is None else float(ex.productivite.get(t, 0.0))
            ly = float(np.log(A["pib"][t]))
            base_f = ALPHA_K * np.log(k_agg) + (1 - ALPHA_K) * np.log(n_star) + cum_prod
            if ex.lpgf is not None and t in ex.lpgf.index:
                gap_t = ly - (float(ex.lpgf[t]) + base_f)
            else:
                gap_t = -OKUN * (u_cur - u_star(t)) / 100
            gap_hist[t] = gap_t
            if ex.lpot_ref is not None and t in ex.lpot_ref.index:
                dpot_hist[t] = (ly - gap_t) - float(ex.lpot_ref[t])
                # v0.8 : part de l'écart de potentiel due au capital (endogène à la demande) prise en compte dans
                # l'anticipation (PART_K_ANTICIPATION = 1 : comme en v0.7 ; 0 : seuls les chocs exogènes d'offre)
                if ex.lk_ref is not None and t in ex.lk_ref.index:
                    dk_t = np.log(k_agg) - float(ex.lk_ref[t])
                    dpot_hist[t] -= (1 - _par(ex, "PART_K_ANTICIPATION")) * ALPHA_K * dk_t
            offre = dict(ecart_production=100 * gap_t, pib_potentiel=float(np.exp(ly - gap_t)), lpgf_implicite=ly - gap_t - base_f,
                         emploi_structurel=n_star, capital_marchand=k_agg)
            hist_vol[t] = {"C": self.dem["C"], "X": self.dem["X"], "I": self.dem["I"], "G": self.dem["G"], "M": Mtot,
                           "q": dict(q_br), "q_nm": q_nm, "n_nm": n_nm, "u": u_cur}
            etat["phi"] = phi
            fp = self._finances(t, A, niv, mb, ab, ex, w, n_br, n_nm, pc, pib_vol, q_br, pva)
            tuc_m = sum(self._tuc(b, t, q_br[b], H) * H[b]["q"][B] for b in S.TUC_BRANCHE) / sum(H[b]["q"][B] for b in S.TUC_BRANCHE)
            IND = [b for b in BR if b.startswith("C")]
            ind_nom = sum(q_br[b] / H[b]["q"][B] * self.hist[b].va_cp[B] * pva[b] / H[b]["pva"][B] for b in IND)
            ind_B = sum(self.hist[b].va_cp[B] for b in IND)
            part_ind = 100 * ind_B / m.pib_cp[B] * (ind_nom / ind_B) / A["pib_nom_idx"][t]
            # comptes d'agents (audit 2026) : RNB, épargne et capacité de financement des ménages, solde extérieur
            if not hasattr(self, "_rp0"):
                import m14_heterogeneite as H14
                self._rp0 = H14.revenus_primaires_nets(B)
            rev_prim = self._rp0 * fp["pib_nominal"] - fp["dividendes_non_residents"]
            c_nom = C_cn * pc
            i_men_nom = float(dl.i_cp[B]) * Imen / A["Imen"][B] * pi_idx
            ext = dict(rnb=fp["pib_nominal"] + rev_prim, revenus_primaires_nets=rev_prim, epargne_menages=rdb - c_nom,
                       taux_epargne=100 * (rdb - c_nom) / rdb, investissement_menages=i_men_nom,
                       capacite_menages=rdb - c_nom - i_men_nom, solde_exterieur=px * X_cn - pm_agg * M_cn + rev_prim)
            res.append(dict(annee=t, **ext, **offre, part_industrie=part_ind, emploi_industrie=sum(n_br[b] for b in IND),
                            vol_industrie=sum(q_br[b] for b in IND) / sum(H[b]["q"][B] for b in IND), supplement_demande_fermeture=Z_dem, tuc_industrie=tuc_m, revenus_patrimoine_menages=A["d4"][t], ebe_menages=A["ebe"][t], pib=A["pib"][t], c=C_cn, x=X_cn, m=M_cn, fbcf=m.fbcf[B] * I_tot / dem0["I"], emploi=emploi, chomage=u_cur,
                            salaire=w, pc=pc, pva_m=pva_m, px=px, rdb=rdb, phi=phi, **fp))
        self.H, self.A = H, A
        E.SIGMA_TRAVAIL, E.PHILLIPS = sauv_glob
        return pd.DataFrame(res).set_index("annee")

    def _leontief_base(self, dem):
        self.dem = dem
        x, M, Ad, Am = self._leontief(1.0, np.ones(len(self.P)))
        return x, M, Ad, Am

    # ---------------------------------------------------------------------------------------------------------------
    def _rdb(self, t, w, n_br, niv, hist_vol, A, ex, pc, mb):
        """Revenu disponible brut des ménages (M€ courants), composantes indexées :
        rémunérations ∝ masse salariale (salaire par tête × emploi salarié, toutes branches, non marchand compris) ;
        revenu mixte et loyers imputés, revenus du patrimoine, transferts divers, autres ∝ PIB nominal (approché) ;
        prestations : indexées sur les prix de l'année précédente × volume exogène + allocations chômage ∝ chômeurs ;
        cotisations ∝ rémunérations ; impôts ∝ (rémunérations + revenu mixte + patrimoine + prestations)."""
        B = self.B
        emploi_t = sum(n_br.values()) + niv["n_nm"] + self._extra(ex, "emploi_additionnel", t)
        masse = (w / A["w"][B]) * (emploi_t / A["emploi"][B])
        pib_nom = A["pib_nom_idx"][t]                         # PIB nominal (indice, base B)
        prest = (A["pc"][t - 1] / A["pc"][B]) * float(ex.prestations_volume[t]) / float(ex.prestations_volume[B])
        d1 = mb.d1 * masse + (_niv(ex, "salaire_public", t)) * self.apu.loc[B].d1pay * (w / A["w"][B]) * (niv["n_nm"] / self.n_nm0)
        d1 += ((EXP["wpub"](t) if "wpub" in EXP else 1.0) - 1.0) * self.apu.loc[B].d1pay * (w / A["w"][B]) * (niv["n_nm"] / self.n_nm0)
        ebe, d4 = self._revenus_patrimoine(t, A, ex, pc)
        autres = ebe + d4 + (mb.d7 + mb.autres) * pib_nom
        mm = ex.mesure_menages or {}
        d62 = mb.d62 * prest + self._extra(ex, "ajust_prestations", t) + mm.get("prestations", 0.0) * self._idx_mesure(mm, pib_nom, t) \
            + self._are(ex, t, niv, A, emploi_t)
        autres += self._profits(ex, t, pib_nom)["menages"]
        d61 = mb.d61 * masse * (1 if ex.taux_cotisations is None else float(ex.taux_cotisations.get(t, 1.0)))
        base_imp = (mb.d1 * masse + ebe + d4 + d62)
        d5 = mb.d5 * base_imp / (mb.d1 + mb.ebe + mb.d4 + mb.d62) + mm.get("impots", 0.0) * self._idx_mesure(mm, pib_nom, t) \
            + _niv(ex, "impots_menages_pib", t) / 100 * self.macro.pib_cp[self.B] * pib_nom
        return d1 + autres + d62 - d61 - d5

    def _are(self, ex, t, niv, A, emploi_t):
        """v0.7 : variation des allocations chômage due à la variation du nombre de chômeurs par rapport à l'année de base
        (M€ courants, indexées sur le salaire moyen). Stabilisateur automatique."""
        B = self.B
        if not hasattr(self, "_chom0"):
            self._chom0 = float(self.macro.chomage[B]) / 100 * float(A["emploi"][B]) / (1 - float(self.macro.chomage[B]) / 100)
        pa = float(ex.population_active[t]) if t in ex.population_active.index else emploi_t / (1 - 0.075)
        chom = max(pa - emploi_t, 0.0)
        if "chom_ref" in EXP:   # phase 3.2 : backtest, prestations observées incluant déjà le chômage observé
            ref = EXP["chom_ref"](self, t)
            return DEPENSE_ARE_BASE * float(self.macro.pib_cp[B]) * ((chom - ref) / self._chom0) * (A["w"].get(t, A["w"][t - 1]) / A["w"][B])
        return DEPENSE_ARE_BASE * float(self.macro.pib_cp[B]) * (chom / self._chom0 - 1) * (A["w"].get(t, A["w"][t - 1]) / A["w"][B])

    def _profits(self, ex, t, pib_nom=None):
        """Supplément de profits après impôt dû aux mesures (M€ courants) et sa répartition (M14) : dividendes reçus par
        les ménages résidents, versés aux non-résidents, conservés par les entreprises."""
        mm = ex.mesure_menages or {}
        g = mm.get("profits", 0.0)
        if not g:
            return {"menages": 0.0, "non_residents": 0.0, "conserve": 0.0, "autres_residents": 0.0}
        if pib_nom is None:
            pib_nom = self.A_courant["pib_nom_idx"][t]
        import m14_heterogeneite as H14
        montee = min(1.0, max(0.0, (t - mm.get("debut", 0) + 1) / 3))    # distribution progressive (3 ans)
        part = H14.DISTRIBUTION_PROFITS[mm.get("variante_distribution", "central")] * montee
        return H14.dividendes_menages(g * self._idx_mesure(mm, pib_nom, t), part)

    def _conso_effectif(self, ex, t):
        """Correction du revenu pris en compte par l'équation de consommation (M14) : profil des propensions par décile
        appliqué aux gains et pertes de la microsimulation, propension du dernier centile pour les dividendes."""
        mm = ex.mesure_menages or {}
        if not mm:
            return 0.0
        import m14_heterogeneite as H14
        pib_nom = self.A_courant["pib_nom_idx"][t]
        v = mm.get("conso", 0.0) * self._idx_mesure(mm, pib_nom, t)
        v += self._profits(ex, t, pib_nom)["menages"] * (H14.facteur_top1(mm.get("variante_pmc", "central")) - 1)
        return v

    def _tuc(self, b, t, q, H):
        """TUC simulé : TUC_B × (production / production de base) / (capacité / capacité de base), capacité ∝ capital
        installé en début d'année × exp(g_cap (t − B))."""
        B = self.B
        cap = (H[b]["k"][t - 1] / H[b]["k"][B - 1]) * np.exp(self.g_cap[b] * (t - B))
        return self.tuc_B[b] * (q / H[b]["q"][B]) / cap

    def _idx_mesure(self, mm, pib_nom, t):
        """Montant d'une mesure évaluée sur les revenus de l'année mm["annee"], indexé sur le PIB nominal simulé ;
        nul avant l'année mm["debut"]."""
        if t < mm.get("debut", 0):
            return 0.0
        a = mm.get("annee", self.B)
        return pib_nom * self.macro.pib_cp[self.B] / self.macro.pib_cp[a]

    @staticmethod
    def _extra(ex, nom, t):
        if nom == "emploi_additionnel" and ex.fermeture_offre:
            return 0.0      # avec fermeture d'offre, les actifs supplémentaires sont absorbés par la production
        v = getattr(ex, nom, None)
        return 0.0 if v is None else float(v.get(t, 0.0))

    def _revenus_patrimoine(self, t, A, ex, pc):
        """Excédent et revenu mixte, revenus de la propriété nets des ménages.
        Par défaut : indexés sur le PIB nominal. Option `Exogenes.patrimoine_endogene` : équations estimées (lot 7), qui
        dégradent la rétrosimulation 2015-2019 (revenu disponible −2,3 % au lieu de +0,1 %, la hausse des dividendes de
        2018 liée au prélèvement forfaitaire unique n'étant pas expliquée) et n'améliorent que peu 2023-2024."""
        if not ex.patrimoine_endogene:
            idx = A["pib_nom_idx"][t]
            return [self.men.ebe[self.B] * idx, self.men.d4[self.B] * idx]
        out = []
        pibn_t = self.macro.pib_cp[self.B] * A["pib_nom_idx"][t]
        pibn_1 = self.macro.pib_cp[self.B] * A["pib_nom_idx"][t - 1] if (t - 1) in A["pib_nom_idx"] and t - 1 > self.B else self.macro.pib_cp[t - 1]
        r1 = float(ex.taux_long.get(t - 1, ex.taux_long.iloc[-1]))
        for poste in ("ebe", "d4"):
            rr = self.eq["revenus_" + poste].res.params
            y1 = A[poste][t - 1]
            dy = (rr["const"] + rr["dpibn"] * np.log(pibn_t / pibn_1) + rr["dpc"] * np.log(pc / A["pc"][t - 1])
                  + rr["ecm_1"] * (np.log(y1) - np.log(pibn_1)) + rr["r_1"] * r1)
            out.append(y1 * np.exp(dy + self.c_rev[poste]))
        return out

    def _finances(self, t, A, niv, mb, ab, ex, w, n_br, n_nm, pc, pib_vol, q_br, pva):
        """Administrations publiques, taux apparents de l'année de base. Recettes :
        impôts sur la production et les importations ∝ consommation nominale ; impôts sur le revenu et le patrimoine =
        part ménages (∝ base imposable des ménages) + impôt sur les sociétés (∝ EBE des branches marchandes × taux d'IS) ;
        cotisations ∝ masse salariale ; autres recettes ∝ PIB nominal. Dépenses : rémunérations publiques ∝ salaire moyen
        × emploi non marchand ; autres consommations ∝ volume × prix ; prestations ; intérêts = taux apparent × dette."""
        B = self.B
        emploi_t = sum(n_br.values()) + n_nm + self._extra(ex, "emploi_additionnel", t)
        masse = (w / A["w"][B]) * (emploi_t / A["emploi"][B])
        pib_nom = A["pib_nom_idx"][t]
        cons_nom = A["C"][t] / A["C"][B] * pc / A["pc"][B]
        prest = (A["pc"][t - 1] / A["pc"][B]) * float(ex.prestations_volume[t]) / float(ex.prestations_volume[B])
        # EBE des branches marchandes (approché : VA nominale − rémunérations imputées)
        ebe_m = sum(q_br[b] * pva[b] for b in self.BR) - sum(self.H[b]["cn"][B] * w / A["w"][B] * n_br[b] for b in self.BR)
        ebe_m0 = sum(self.hist[b].va_cp[B] for b in self.BR) - sum(self.hist[b].wb[B] / self.hist[b].ns[B] * self.hist[b].n[B] for b in self.BR)
        tau, tau0 = float(ex.taux_is.get(t, ex.taux_is.iloc[-1])), float(ex.taux_is.get(B, 25.0))
        is0 = 0.15 * ab.d5rec                                   # part de l'IS dans les impôts courants sur le revenu (≈ 15 % ; ordre de grandeur, à caler sur les comptes de l'État)
        # v0.7 : transfert de bénéfices des groupes (semi-élasticité de la base au taux)
        is_t = is0 * (ebe_m / ebe_m0) * (tau / tau0) * (1 - _par(ex, "PART_IS_MULTINAT") * (1 - np.exp(-_par(ex, "SEMI_ELAST_IS") * (tau - tau0) / 100)))
        mm = ex.mesure_menages or {}
        d5_men = (ab.d5rec - is0) * (mb.d1 * masse + A["ebe"][t] + A["d4"][t] + mb.d62 * prest) / (mb.d1 + mb.ebe + mb.d4 + mb.d62)
        d5_men += mm.get("impots", 0.0) * self._idx_mesure(mm, pib_nom, t) + _niv(ex, "impots_menages_pib", t) / 100 * self.macro.pib_cp[self.B] * pib_nom
        d2 = ab.d2rec * cons_nom * (1 + _niv(ex, "impots_produits", t))
        d61 = ab.d61rec * masse * (1 if ex.taux_cotisations is None else float(ex.taux_cotisations.get(t, 1.0)))
        autres_r = (ab.tr - ab.d2rec - ab.d5rec - ab.d61rec) * pib_nom
        tr = d2 + d5_men + is_t + d61 + autres_r
        d1p = ab.d1pay * (w / A["w"][B]) * (n_nm / self.n_nm0) * (1 + _niv(ex, "salaire_public", t)) * (EXP["wpub"](t) if "wpub" in EXP else 1.0)
        g_vol = float(ex.conso_publique[t]) / float(ex.conso_publique[B])
        p3_autres = (ab.p3 - ab.d1pay) * g_vol * pc / A["pc"][B]
        d62 = ab.d62pay * prest + self._extra(ex, "ajust_prestations", t) + mm.get("prestations", 0.0) * self._idx_mesure(mm, pib_nom, t) \
            + self._are(ex, t, niv, A, emploi_t)
        # taux apparent de la dette : rejoint progressivement le taux de marché (renouvellement d'environ 1/8 de la dette par an)
        if "taux_app" not in niv:
            niv["taux_app"] = ab.d41pay / self.apu.dette[B - 1]
        _tm = EXP["taux_emission"](t) if "taux_emission" in EXP else max(float(ex.taux_long.get(t, ex.taux_long.iloc[-1])), 0.0) / 100
        niv["taux_app"] += (_tm - niv["taux_app"]) / EXP.get("renouv", 8)
        d41 = niv["taux_app"] * niv["dette"]
        ratio0 = (ab.te - ab.p3 - ab.d62pay - ab.d41pay) / self.macro.pib_cp[B]
        ratio = ratio0 if ex.autres_depenses_pib is None else float(ex.autres_depenses_pib.get(t, ratio0))
        autres_d = ratio * self.macro.pib_cp[B] * pib_nom      # subventions, investissement public, autres transferts
        pibn = self.macro.pib_cp[B] * pib_nom
        tr += _cal(ex, "recettes", t) / 100 * pibn
        te = d1p + p3_autres + d62 + d41 + autres_d + _cal(ex, "depenses", t) / 100 * pibn
        solde = tr - te
        niv["dette"] = niv["dette"] - solde + _cal(ex, "dette", t)
        return dict(recettes=tr, depenses=te, solde=solde, solde_pib=solde / pibn * 100, dette=niv["dette"], dette_pib=niv["dette"] / pibn * 100,
                    is_=is_t, dividendes_non_residents=self._profits(ex, t, pib_nom)["non_residents"], cotisations=d61, tva_etc=d2, prestations=d62, interets=d41, pib_nominal=pibn,
                    taux_apparent=niv["taux_app"] * 100)


def exogenes_observes(mod: Modele, annees) -> Exogenes:
    """Exogènes observés (pour les tests rétrospectifs)."""
    m, T = mod.macro, mod.tables
    an = list(range(mod.B - 3, max(annees) + 1))
    pm = {}
    for p in mod.P:
        idx, v = {mod.B: 1.0}, 1.0
        for t in range(mod.B + 1, max(annees) + 1):
            c = float(T["OFFRE"].get(("P7", p, str(t)), np.nan)); y = float(T["OFFRE_PYP"].get(("P7", p, str(t)), np.nan))
            g = c / y if (c > 50 and y > 0) else (m.p_m[t] / m.p_m[t - 1])
            v *= g; idx[t] = v
        pm[p] = idx
    prix_import = pd.DataFrame(pm)
    em = mod.emp
    pop_act = em.emploi / (1 - m.chomage.reindex(em.index) / 100)
    from statsmodels.tsa.filters.hp_filter import hpfilter
    _, u_star = hpfilter(m.chomage.loc[1980:2025].dropna(), lamb=100)
    autres_I = (m.fbcf - sum(mod.panel[mod.panel.branche == b].set_index("annee").i for b in S.BRANCHES))
    # hors investissement des ménages (endogène, équation de logement) : volume = valeur / prix de la FBCF
    dl = mod.eq["logement"].data
    autres_I = (autres_I - (dl.i_cp / m.p_fbcf.reindex(dl.index)).reindex(autres_I.index)).dropna()
    men = mod.men
    prest_vol = (men.d62 / (m.p_c.reindex(men.index).shift(1))).ffill()
    apu = mod.apu
    autres_dep = (apu.te - apu.p3 - apu.d62pay - apu.d41pay) / m.pib_cp
    return Exogenes(autres_depenses_pib=autres_dep, demande_mondiale=m.ue_m, prix_mondial=m.p_ue_m, prix_import=prix_import, conso_publique=m.g,
                    autres_investissements=autres_I, population_active=pop_act, chomage_structurel=u_star,
                    taux_long=m.taux_long, taux_is=S.taux_is(), prestations_volume=prest_vol)


def exogenes_projection(mod: Modele, annees, **modifs) -> Exogenes:
    """Compte central conventionnel (et non une prévision) : exogènes prolongés à des rythmes moyens.
    Demande mondiale +3 %/an, prix mondiaux et d'importation +1,5 %/an, consommation publique et autres investissements
    +1 %/an en volume, population active +0,3 %/an, chômage structurel 7,5 %, taux long 3,2 %, taux d'IS inchangé,
    prestations +1,2 %/an en volume (vieillissement), dépenses publiques autres constantes en part du PIB ;
    fermeture d'offre ρ = 0,15 avec amortissement 0,3 (décision A12 ; ρ = 0 pour le modèle de demande pur)."""
    B, m = mod.B, mod.macro
    ans = list(range(B - 3, max(annees) + 1))
    obs = exogenes_observes(mod, [B])
    def prol(serie, g):
        s = serie.copy().astype(float)
        for t in ans:
            if t > B:
                s[t] = s[t - 1] * (1 + g)
        return s
    pm = pd.DataFrame({p: {t: (1.015 ** (t - B) if t >= B else 1.0) for t in ans} for p in mod.P})
    ex = Exogenes(demande_mondiale=prol(m.ue_m, 0.03), prix_mondial=prol(m.p_ue_m, 0.015), prix_import=pm,
                  conso_publique=prol(m.g, 0.01), autres_investissements=prol(obs.autres_investissements, 0.01),
                  population_active=prol(obs.population_active, 0.003),
                  chomage_structurel=pd.Series({t: 7.5 for t in ans}), taux_long=pd.Series({t: (m.taux_long[t] if t <= B else 3.2) for t in ans}),
                  taux_is=pd.Series({t: (S.taux_is().get(t, 25.83)) for t in ans}), prestations_volume=prol(obs.prestations_volume, 0.012),
                  fermeture_offre=RHO_DEFAUT)
    for k, v in modifs.items():
        setattr(ex, k, v)
    return ex
