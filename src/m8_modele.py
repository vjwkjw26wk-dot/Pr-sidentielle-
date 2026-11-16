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
import pandas as pd

import m5_productif as m5
import m7_equations as E
import m7_series as S
from telechargement import jsonstat_dict, telecharger

PRODUITS_NM = ["CPA_L68A", "CPA_L68B", "CPA_O", "CPA_P", "CPA_Q86", "CPA_Q87_88"]
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
    autres_investissements: pd.Series      # volume (M€ de base) : logement, administrations, branches non marchandes
    population_active: pd.Series           # milliers
    chomage_structurel: pd.Series          # %
    taux_long: pd.Series                   # %
    taux_is: pd.Series                     # %
    prestations_volume: pd.Series          # croissance en volume des prestations (hors chômage), indice
    duree_travail: pd.Series = None        # non utilisé en v0.1
    parts_importees: dict = field(default_factory=dict)   # réindustrialisation : {produit: facteur sur la part importée}
    phi_impose: pd.Series = None           # facteur commun des parts importées imposé (repris d'un compte central)
    choc_salaire: pd.Series = None         # hausse exogène du salaire (log), par année
    taux_cotisations: pd.Series = None     # taux apparent de cotisations sociales (si mesure)
    autres_depenses_pib: pd.Series = None  # dépenses publiques hors consommation, prestations et intérêts, en part du PIB (mesures)
    productivite: pd.Series = None         # écart à la tendance de productivité par tête des branches (points de log par an)


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
                                                       + rp["ecm_1"] * (lpva[t - 1] - lclu[t - 1])))
                res_i.append((li[t] - li[t - 1]) - (ri["dlq"] * (lq[t] - lq[t - 1]) + ri["dlq_1"] * (lq[t - 1] - lq[t - 2])
                                                   + ri["li_1"] * li[t - 1] + ri["lk_1"] * lk[t - 1] + ri["lq_1"] * lq[t - 1]))
            self.c_emp[b], self.c_prix[b], self.c_inv[b] = map(lambda v: float(np.mean(v)), (res_e, res_p, res_i))

    # ---------------------------------------------------------------------------------------------------------------
    def _leontief(self, phi, fact_imp):
        """Production et importations pour une demande finale par catégorie (volumes, prix de base)."""
        n = len(self.P)
        pim = np.clip(self.part_imp_ci * phi * fact_imp[:, None], 0, 1)
        Am = self.Atot * pim
        Ad = self.Atot - Am
        fd = np.zeros(n)
        fm = np.zeros(n)
        for k in CAT:
            v = self.struct[k] * self.dem[k]
            sh = np.clip(self.part_imp[k] * (phi if k != "X" else 1.0) * fact_imp, 0, 1)
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
             "X": {t: m.x[t] for t in range(B - 3, B + 1)}, "M": {t: m.m[t] for t in range(B - 3, B + 1)},
             "u": {t: m.chomage[t] for t in range(B - 3, B + 1)},
             "px": {t: m.p_x[t] for t in range(B - 3, B + 1)}, "pm_agg": {t: m.p_m[t] for t in range(B - 3, B + 1)},
             "ppib": {t: m.p_pib[t] for t in range(B - 3, B + 1)}, "pib": {t: m.pib[t] for t in range(B - 3, B + 1)},
             "emploi": {t: em.emploi[t] for t in range(B - 3, B + 1)}}
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
        fact_imp = np.array([ex.parts_importees.get(p, 1.0) for p in P])
        for t in annees:
            # valeurs initiales de l'itération : celles de l'année précédente
            prev = hist_vol[t - 1]
            C, X, phi = prev["C"], prev["X"], etat["phi"]
            I_br = {b: H[b]["i"][t - 1] for b in BR}
            q_br = dict(prev["q"])
            n_br = {b: H[b]["n"][t - 1] for b in BR}
            w = A["w"][t - 1]
            pva = {b: H[b]["pva"][t - 1] for b in BR}
            for it in range(iterations):
                # ---- 1. prix
                pm = np.array([float(ex.prix_import.loc[t, p]) if p in ex.prix_import.columns else 1.0 for p in P])
                w_idx = w / A["w"][B]
                pva_prod = np.array([pva[b] / H[b]["pva"][B] if b in pva else w_idx for b in self.br_prod])
                pp = self._prix(pva_prod, pm)
                def pfin(k):
                    v = self.struct[k] * self.tot[k]
                    sh = self.part_imp[k] * phi
                    return float(((v * (1 - sh) * pp).sum() + (v * sh * pm).sum()) / v.sum())
                pc_idx, px_idx, pi_idx = pfin("C"), pfin("X"), pfin("I")
                pc = m.p_c[B] * pc_idx
                px = m.p_x[B] * px_idx
                pm_agg = m.p_m[B] * float((pm * (self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT))).sum() / (self.Am0 @ self.x0 + sum(self.Fm[k] for k in CAT)).sum())
                # ---- 2. salaires (secteur marchand, par tête)
                qm = sum(q_br.values()); nm = sum(n_br.values())
                prod_m = qm / nm
                vam = sum(q_br[b] * pva[b] for b in BR)
                pva_m = vam / qm
                u_prev = hist_vol[t - 1]["u"]
                rw = r["salaires"]
                ugap = u_prev - float(ex.chomage_structurel.get(t, ex.chomage_structurel.iloc[-1]))
                dlw = (rw["const"] + rw["dlpc"] * np.log(pc / A["pc"][t - 1]) + rw["dlprod"] * np.log(prod_m / A["prod_m"][t - 1])
                       + rw["ecm_1"] * (np.log(A["w"][t - 1]) - np.log(A["pva_m"][t - 1]) - np.log(A["prod_m"][t - 1])) + E.PHILLIPS * ugap)
                if ex.choc_salaire is not None:
                    dlw += float(ex.choc_salaire.get(t, 0.0))
                w_new = A["w"][t - 1] * np.exp(dlw)
                # ---- 3. prix de la valeur ajoutée et emploi par branche
                re, rp, ri = r["emploi"], r["prix_va"], r["investissement"]
                pva_new, n_new, I_new = {}, {}, {}
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
                          + re["ecm_1"] * (np.log(hb["n"][t - 1]) - lq1 + E.SIGMA_TRAVAIL * lrc1 + self.g_prod[b] * (t - 1 - B))
                          - (g_b - self.g_prod[b]))
                    n_new[b] = hb["n"][t - 1] * np.exp(dn)
                    # prix de la VA
                    clu = cn * n_new[b] / q_br[b]
                    clu1 = cn_1 * hb["n"][t - 1] / hb["q"][t - 1]
                    dp = self.c_prix[b] + rp["dlclu"] * np.log(clu / clu1) + rp["dlq"] * (lq - lq1) + rp["ecm_1"] * (np.log(hb["pva"][t - 1]) - np.log(clu1))
                    pva_new[b] = hb["pva"][t - 1] * np.exp(dp)
                    # investissement (accélérateur) + coût d'usage
                    di = (self.c_inv[b] + ri["dlq"] * (lq - lq1) + ri["dlq_1"] * (lq1 - lq2) + ri["li_1"] * np.log(hb["i"][t - 1])
                          + ri["lk_1"] * np.log(hb["k"][t - 1]) + ri["lq_1"] * lq1)
                    I_new[b] = hb["i"][t - 1] * np.exp(di)
                # effet du coût d'usage (IS, taux) : élasticité de long terme agrégée, ajustement à la vitesse des branches
                tau = float(ex.taux_is.get(t, ex.taux_is.iloc[-1])); tau0 = float(ex.taux_is.get(B, tau))
                rr_ = float(ex.taux_long.get(t, ex.taux_long.iloc[-1])); rr0 = float(ex.taux_long.get(B, rr_))
                lcu = np.log((max(rr_, -5) / 100 + E.DELTA_USAGE) / (1 - tau / 100)) - np.log((max(rr0, -5) / 100 + E.DELTA_USAGE) / (1 - tau0 / 100))
                eps_cu = self.eq["investissement_snf"].lr["long terme : élasticité au coût d'usage du capital"]
                cible = np.exp(eps_cu * lcu)
                ajust = 1 - (1 + ri["li_1"]) ** (t - B)            # convergence progressive vers l'effet de long terme
                I_new = {b: v * cible ** ajust / (etat.get("cible_prec", 1.0) if False else 1.0) for b, v in I_new.items()}
                # PIB nominal (indice, base B) : VA marchande en valeur + VA non marchande (volume × salaire)
                q_nm_c = hist_vol[t - 1]["q_nm"] if it == 0 else q_nm
                vm = sum(q_br[b] / H[b]["q"][B] * self.hist[b].va_cp[B] * pva_new[b] / H[b]["pva"][B] for b in BR)
                vm0 = sum(self.hist[b].va_cp[B] for b in BR)
                s_m = sum(self.va_br0[b] for b in BR) / sum(self.va_br0.values())
                idx_nom = s_m * vm / vm0 + (1 - s_m) * (q_nm_c / self.va_br0["NM"]) * (w_new / A["w"][B])
                vol_m = sum(q_br[b] for b in BR) / sum(H[b]["q"][B] for b in BR)
                idx_vol = s_m * vol_m + (1 - s_m) * q_nm_c / self.va_br0["NM"]
                A["pib_nom_idx"] = A.get("pib_nom_idx", {B: 1.0})
                A["pib_nom_idx"][t] = idx_nom
                ppib_est = m.p_pib[B] * idx_nom / idx_vol
                # ---- 4. demande finale
                rc = r["consommation"]
                rdb = self._rdb(t, w_new, n_new, niv, hist_vol, A, ex, pc, mb)
                rdbr, rdbr1 = rdb / pc, A["rdb"][t - 1] / A["pc"][t - 1]
                u_cur = prev["u"] if it == 0 else u_cur
                dC = rc["const"] + rc["dlrdb"] * np.log(rdbr / rdbr1) + rc["du"] * (u_cur - prev["u"]) + rc["ecart_1"] * (np.log(A["C"][t - 1]) - np.log(rdbr1))
                C_cn = A["C"][t - 1] * np.exp(dC)
                rx = r["exportations"]
                pw = float(ex.prix_mondial[t]) / float(ex.prix_mondial[t - 1])
                dX = rx["const"] + rx["dldm"] * np.log(float(ex.demande_mondiale[t]) / float(ex.demande_mondiale[t - 1])) + rx["dlprel"] * (np.log(px / A["px"][t - 1]) - np.log(pw))
                X_cn = A["X"][t - 1] * np.exp(dX)
                G_idx = float(ex.conso_publique[t]) / float(ex.conso_publique[B])
                fbcf_br = sum(I_new[b] / self.hist[b].i[B] * self.hist[b].i_cp[B] for b in BR) * conv_I
                I_tot = fbcf_br + I_autres_B * float(ex.autres_investissements[t]) / float(ex.autres_investissements[B])
                self.dem = {"C": dem0["C"] * C_cn / m.c[B], "G": dem0["G"] * G_idx, "I": I_tot, "S": dem0["S"], "X": dem0["X"] * X_cn / m.x[B]}
                # ---- 5. importations (équation agrégée) et production
                rm = r["importations"]
                D = sum(w_ * v for w_, v in zip(E.CONTENU_IMPORT.values(), (self.dem["C"] / dem0["C"] * m.c[B], self.dem["G"] / dem0["G"] * m.g[B],
                                                                            (self.dem["I"] + self.dem["S"]) / (dem0["I"] + dem0["S"]) * m.fbc[B], X_cn)))
                lprel, lprel1 = np.log(pm_agg / ppib_est), np.log(A["pm_agg"][t - 1] / A["ppib"][t - 1])
                dM = (rm["const"] + rm["dld"] * np.log(D / A["D"][t - 1]) + rm["dlprel"] * (lprel - lprel1) + rm["lm_1"] * np.log(A["M"][t - 1])
                      + rm["ld_1"] * np.log(A["D"][t - 1]) + rm["lprel_1"] * lprel1 + rm["t"] * (t - 2010))
                M_cn = A["M"][t - 1] * np.exp(dM)
                M_cible = M_B * M_cn / m.m[B]
                lo, hi = 0.3, 3.0
                for _ in range(40):
                    phi_ = 0.5 * (lo + hi)
                    x, Mtot, Ad, Am = self._leontief(phi_, fact_imp)
                    if Mtot > M_cible:
                        hi = phi_
                    else:
                        lo = phi_
                if ex.phi_impose is not None:
                    # variante de réindustrialisation : comportement d'importation des autres produits inchangé (facteur
                    # commun repris du compte central), parts importées des produits ciblés réduites
                    phi_ = float(ex.phi_impose[t])
                    x, Mtot, Ad, Am = self._leontief(phi_, fact_imp)
                    M_cn = m.m[B] * Mtot / M_B
                va_prod = self.av * x
                q_new = {b: H[b]["q"][B] * va_prod[self.br_prod == b].sum() / self.va_br0[b] for b in BR}
                q_nm = va_prod[self.br_prod == "NM"].sum()
                n_nm = self.n_nm0 * q_nm / self.va_br0["NM"]
                emploi = sum(n_new.values()) + n_nm
                u_new = 100 * (1 - emploi / float(ex.population_active[t]))
                # ---- amortissement et convergence
                ecart = abs(np.log(sum(q_new.values()) / sum(q_br.values()))) + abs(np.log(w_new / w)) + abs(u_new - u_cur) / 100
                q_br = {b: q_br[b] ** (1 - amorti) * q_new[b] ** amorti for b in BR}
                n_br, pva, w, phi, u_cur = n_new, pva_new, w_new, phi_, u_new
                if ecart < 1e-7 and it > 2:
                    break
            # ---- enregistrement de l'année t
            for b in BR:
                hb = H[b]
                hb["q"][t], hb["n"][t], hb["pva"][t], hb["i"][t] = q_br[b], n_br[b], pva[b], I_new[b]
                hb["cn"][t] = hb["cn"][B] * w / A["w"][B]
                delta = 1 - (self.hist[b].k[B] - self.hist[b].i[B]) / self.hist[b].k[B - 1]
                hb["k"][t] = hb["k"][t - 1] * (1 - delta) + I_new[b]
            A["w"][t], A["pva_m"][t], A["prod_m"][t], A["pc"][t] = w, pva_m, prod_m, pc
            A["C"][t], A["rdb"][t], A["X"][t], A["M"][t], A["u"][t] = C_cn, rdb, X_cn, M_cn, u_cur
            A["px"][t], A["pm_agg"][t], A["D"][t], A["ppib"][t] = px, pm_agg, D, ppib_est
            pib_vol = (sum(q_br.values()) / sum(H[b]["q"][B] for b in BR) * sum(self.va_br0[b] for b in BR) + q_nm) / sum(self.va_br0.values())
            A["pib"][t] = m.pib[B] * pib_vol
            A["emploi"][t] = emploi
            hist_vol[t] = {"C": self.dem["C"], "X": self.dem["X"], "I": self.dem["I"], "G": self.dem["G"], "M": Mtot,
                           "q": dict(q_br), "q_nm": q_nm, "n_nm": n_nm, "u": u_cur}
            etat["phi"] = phi
            fp = self._finances(t, A, niv, mb, ab, ex, w, n_br, n_nm, pc, pib_vol, q_br, pva)
            res.append(dict(annee=t, pib=A["pib"][t], c=C_cn, x=X_cn, m=M_cn, fbcf=m.fbcf[B] * I_tot / dem0["I"], emploi=emploi, chomage=u_cur,
                            salaire=w, pc=pc, pva_m=pva_m, px=px, rdb=rdb, phi=phi, **fp))
        self.H, self.A = H, A
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
        emploi_t = sum(n_br.values()) + niv["n_nm"]
        masse = (w / A["w"][B]) * (emploi_t / A["emploi"][B])
        pib_nom = A["pib_nom_idx"][t]                         # PIB nominal (indice, base B)
        prest = (A["pc"][t - 1] / A["pc"][B]) * float(ex.prestations_volume[t]) / float(ex.prestations_volume[B])
        d1 = mb.d1 * masse
        autres = (mb.ebe + mb.d4 + mb.d7 + mb.autres) * pib_nom
        d62 = mb.d62 * prest
        d61 = mb.d61 * masse * (1 if ex.taux_cotisations is None else float(ex.taux_cotisations.get(t, 1.0)))
        base_imp = (mb.d1 * masse + mb.ebe * pib_nom + mb.d4 * pib_nom + d62)
        d5 = mb.d5 * base_imp / (mb.d1 + mb.ebe + mb.d4 + mb.d62)
        return d1 + autres + d62 - d61 - d5

    def _finances(self, t, A, niv, mb, ab, ex, w, n_br, n_nm, pc, pib_vol, q_br, pva):
        """Administrations publiques, taux apparents de l'année de base. Recettes :
        impôts sur la production et les importations ∝ consommation nominale ; impôts sur le revenu et le patrimoine =
        part ménages (∝ base imposable des ménages) + impôt sur les sociétés (∝ EBE des branches marchandes × taux d'IS) ;
        cotisations ∝ masse salariale ; autres recettes ∝ PIB nominal. Dépenses : rémunérations publiques ∝ salaire moyen
        × emploi non marchand ; autres consommations ∝ volume × prix ; prestations ; intérêts = taux apparent × dette."""
        B = self.B
        emploi_t = sum(n_br.values()) + n_nm
        masse = (w / A["w"][B]) * (emploi_t / A["emploi"][B])
        pib_nom = A["pib_nom_idx"][t]
        cons_nom = A["C"][t] / A["C"][B] * pc / A["pc"][B]
        prest = (A["pc"][t - 1] / A["pc"][B]) * float(ex.prestations_volume[t]) / float(ex.prestations_volume[B])
        # EBE des branches marchandes (approché : VA nominale − rémunérations imputées)
        ebe_m = sum(q_br[b] * pva[b] for b in self.BR) - sum(self.H[b]["cn"][B] * w / A["w"][B] * n_br[b] for b in self.BR)
        ebe_m0 = sum(self.hist[b].va_cp[B] for b in self.BR) - sum(self.hist[b].wb[B] / self.hist[b].ns[B] * self.hist[b].n[B] for b in self.BR)
        tau, tau0 = float(ex.taux_is.get(t, ex.taux_is.iloc[-1])), float(ex.taux_is.get(B, 25.0))
        is0 = 0.15 * ab.d5rec                                   # part de l'IS dans les impôts courants sur le revenu (≈ 15 % ; ordre de grandeur, à caler sur les comptes de l'État)
        is_t = is0 * (ebe_m / ebe_m0) * (tau / tau0)
        d5_men = (ab.d5rec - is0) * (mb.d1 * masse + mb.ebe * pib_nom + mb.d4 * pib_nom + mb.d62 * prest) / (mb.d1 + mb.ebe + mb.d4 + mb.d62)
        d2 = ab.d2rec * cons_nom
        d61 = ab.d61rec * masse * (1 if ex.taux_cotisations is None else float(ex.taux_cotisations.get(t, 1.0)))
        autres_r = (ab.tr - ab.d2rec - ab.d5rec - ab.d61rec) * pib_nom
        tr = d2 + d5_men + is_t + d61 + autres_r
        d1p = ab.d1pay * (w / A["w"][B]) * (n_nm / self.n_nm0)
        g_vol = float(ex.conso_publique[t]) / float(ex.conso_publique[B])
        p3_autres = (ab.p3 - ab.d1pay) * g_vol * pc / A["pc"][B]
        d62 = ab.d62pay * prest
        # taux apparent de la dette : rejoint progressivement le taux de marché (renouvellement d'environ 1/8 de la dette par an)
        if "taux_app" not in niv:
            niv["taux_app"] = ab.d41pay / self.apu.dette[B - 1]
        niv["taux_app"] += (max(float(ex.taux_long.get(t, ex.taux_long.iloc[-1])), 0.0) / 100 - niv["taux_app"]) / 8
        d41 = niv["taux_app"] * niv["dette"]
        ratio0 = (ab.te - ab.p3 - ab.d62pay - ab.d41pay) / self.macro.pib_cp[B]
        ratio = ratio0 if ex.autres_depenses_pib is None else float(ex.autres_depenses_pib.get(t, ratio0))
        autres_d = ratio * self.macro.pib_cp[B] * pib_nom      # subventions, investissement public, autres transferts
        te = d1p + p3_autres + d62 + d41 + autres_d
        solde = tr - te
        niv["dette"] = niv["dette"] - solde
        pibn = self.macro.pib_cp[B] * pib_nom
        return dict(recettes=tr, depenses=te, solde=solde, solde_pib=solde / pibn * 100, dette=niv["dette"], dette_pib=niv["dette"] / pibn * 100,
                    is_=is_t, cotisations=d61, tva_etc=d2)


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
    prestations +1,2 %/an en volume (vieillissement), dépenses publiques autres constantes en part du PIB."""
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
                  taux_is=pd.Series({t: (S.taux_is().get(t, 25.83)) for t in ans}), prestations_volume=prol(obs.prestations_volume, 0.012))
    for k, v in modifs.items():
        setattr(ex, k, v)
    return ex
