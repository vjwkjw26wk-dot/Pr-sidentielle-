"""M5 — Bloc productif sectoriel : tableaux entrées-sorties, modèle de quantités et modèle de prix.

Source : Eurostat, tableau entrées-sorties symétrique produit × produit aux prix de base (naio_10_cp1700), France,
2010-2024, séparé en flux de production intérieure (DOM) et d'importations (IMP) ; même tableau aux prix de l'année
précédente (naio_10_pyp1700, total seulement, 2011-2022) pour les indices de prix.

Nomenclature : 64 produits de la CPA (niveau A64 de la comptabilité nationale), dont l'énergie : B (industries
extractives, y compris pétrole brut et gaz), C19 (cokéfaction et raffinage), D35 (électricité, gaz, vapeur).

Notations (n produits) :
  Zd, Zm : consommations intermédiaires de produits intérieurs et importés (ligne = produit consommé, colonne = produit
           ou branche utilisatrice) ;
  Fd, Fm : emplois finals intérieurs et importés (colonnes : consommation des ménages, des APU, des ISBLSM, FBCF,
           variation de stocks, exportations) ;
  x      : production ; m : importations ; v : lignes de valeur ajoutée et d'impôts nets sur les produits.
Identités contrôlées (tolérance en M€) :
  (I1) x_i = Σ_j Zd_ij + Σ_k Fd_ik          (équilibre ressources-emplois des produits intérieurs)
  (I2) m_i = Σ_j Zm_ij + Σ_k Fm_ik          (équilibre des produits importés)
  (I3) x_j = Σ_i (Zd_ij + Zm_ij) + t_j + VA_j   (coûts de production de chaque branche)
Modèle de quantités (Leontief) : x = (I − Ad)⁻¹ fd, Ad = Zd · diag(x)⁻¹ ; importations m = Am x + fm.
Modèle de prix (coûts) : p = (pm · Am + p_v · av)(I − Ad)⁻¹, av = (t + VA) / x par unité produite ;
  hypothèse : coefficients techniques fixes, marge et coût salarial unitaires exogènes (rendus endogènes par les
  équations de comportement du lot 7).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from telechargement import jsonstat_dict, telecharger  # noqa: E402

B = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"

# Niveau A64 : codes CPA retenus (les agrégats et sous-détails sont exclus pour éviter tout double compte)
A64 = ["CPA_A01", "CPA_A02", "CPA_A03", "CPA_B", "CPA_C10-12", "CPA_C13-15", "CPA_C16", "CPA_C17", "CPA_C18",
       "CPA_C19", "CPA_C20", "CPA_C21", "CPA_C22", "CPA_C23", "CPA_C24", "CPA_C25", "CPA_C26", "CPA_C27", "CPA_C28",
       "CPA_C29", "CPA_C30", "CPA_C31_32", "CPA_C33", "CPA_D", "CPA_E36", "CPA_E37-39", "CPA_F", "CPA_G45", "CPA_G46",
       "CPA_G47", "CPA_H49", "CPA_H50", "CPA_H51", "CPA_H52", "CPA_H53", "CPA_I", "CPA_J58", "CPA_J59_60", "CPA_J61",
       "CPA_J62_63", "CPA_K64", "CPA_K65", "CPA_K66", "CPA_L68A", "CPA_L68B", "CPA_M69_70", "CPA_M71", "CPA_M72",
       "CPA_M73", "CPA_M74_75", "CPA_N77", "CPA_N78", "CPA_N79", "CPA_N80-82", "CPA_O", "CPA_P", "CPA_Q86",
       "CPA_Q87_88", "CPA_R90-92", "CPA_R93", "CPA_S94", "CPA_S95", "CPA_S96", "CPA_T", "CPA_U"]
ENERGIE = ["CPA_B", "CPA_C19", "CPA_D"]
FINALS = ["P3_S14", "P3_S13", "P3_S15", "P51G", "P52", "P53", "P6"]
VA_LIGNES = ["D1", "B2A3G", "D29X39"]          # rémunérations, excédent brut et revenu mixte, autres impôts nets sur la production
LIBELLES_FINALS = {"P3_S14": "Consommation des ménages", "P3_S13": "Consommation des APU", "P3_S15": "Consommation des ISBLSM",
                   "P51G": "FBCF", "P52": "Variation de stocks", "P53": "Objets de valeur", "P6": "Exportations"}


def _charger(nom_fichier: str, url: str) -> pd.Series:
    d = json.loads(telecharger(url, nom_fichier).read_text(encoding="utf-8"))
    s = pd.Series(jsonstat_dict(d))
    return s


def charger_tables(force: bool = False) -> dict:
    out = {}
    for st in ("TOTAL", "DOM", "IMP"):
        url = B + f"naio_10_cp1700?format=JSON&geo=FR&unit=MIO_EUR&stk_flow={st}&sinceTimePeriod=2010"
        s = _charger(f"eurostat_naio_10_cp1700_FR_{st}.json", url)
        s.index.names = ["prd_use", "prd_ava", "time"]  # dimensions variables (stk_flow, unit, geo fixes)
        out[st] = s
    url = B + "naio_10_pyp1700?format=JSON&geo=FR&unit=MIO_EUR&stk_flow=TOTAL&sinceTimePeriod=2011"
    s = _charger("eurostat_naio_10_pyp1700_FR_TOTAL.json", url)
    s.index.names = ["prd_use", "prd_ava", "time"]
    out["PYP"] = s
    # Tableaux des ressources (offre) aux prix courants et de l'année précédente : seule source fiable des importations
    # par produit aux prix de N−1 (la ligne P7 de naio_10_pyp1700 est désalignée pour la France en 2014-2019).
    for cle, tab in (("OFFRE", "naio_10_cp15"), ("OFFRE_PYP", "naio_10_pyp15")):
        s = _charger(f"eurostat_{tab}_FR.json", B + f"{tab}?format=JSON&geo=FR&unit=MIO_EUR&sinceTimePeriod=2010")
        s.index.names = ["ind_impv", "prd_amo", "time"]
        out[cle] = s
    return out


class TableES:
    """Tableau entrées-sorties d'une année, aux prix courants (ou de l'année précédente)."""

    def __init__(self, tables: dict, annee: int, prix: str = "courants"):
        a = str(annee)
        tot = tables["TOTAL"] if prix == "courants" else tables["PYP"]
        self.annee, self.type_prix = annee, prix
        g = lambda s, use, ava: float(s.get((use, ava, a), np.nan))  # noqa: E731
        P = A64
        mat = lambda s, cols: pd.DataFrame([[g(s, c, r) for c in cols] for r in P], index=P, columns=cols).fillna(0.0)  # noqa: E731
        if prix == "courants":
            self.Zd = mat(tables["DOM"], P)
            self.Zm = mat(tables["IMP"], P)
            self.Fd = mat(tables["DOM"], FINALS)
            self.Fm = mat(tables["IMP"], FINALS)
        else:
            self.Z = mat(tot, P)
            self.F = mat(tot, FINALS)
        self.x = pd.Series([g(tot, c, "P1") for c in P], index=P).fillna(0.0)
        self.t = pd.Series([g(tot, c, "D21X31") for c in P], index=P).fillna(0.0)
        self.va = pd.DataFrame({l: [g(tot, c, l) for c in P] for l in VA_LIGNES + ["B1G", "P51C"]}, index=P).fillna(0.0)
        # importations par produit : total des emplois importés (ligne du produit dans la table IMP)
        if prix == "courants":
            self.m = self.Zm.sum(axis=1) + self.Fm.sum(axis=1)
        else:
            self.m = pd.Series([g(tot, "TU", r) for r in P], index=P) - self.x  # ressources totales − production (approx.)
            self.m_tot = pd.Series([g(tot, c, "P7") for c in P], index=P)

    # --- contrôles ------------------------------------------------------------------------------------------
    def identites(self) -> pd.DataFrame:
        I1 = self.Zd.sum(axis=1) + self.Fd.sum(axis=1) - self.x
        I3 = self.Zd.sum(axis=0) + self.Zm.sum(axis=0) + self.t + self.va["B1G"] - self.x
        I3b = self.va[VA_LIGNES].sum(axis=1) - self.va["B1G"]
        return pd.DataFrame({"I1_emplois_moins_production": I1, "I3_couts_moins_production": I3,
                             "VA_composantes_moins_B1G": I3b})

    # --- coefficients et modèles -------------------------------------------------------------------------------
    @property
    def actifs(self) -> list:
        return [p for p in A64 if self.x[p] > 0]

    def coefficients(self):
        P = self.actifs
        x = self.x[P].to_numpy()
        Ad = self.Zd.loc[P, P].to_numpy() / x
        Am = self.Zm.loc[P, P].to_numpy() / x
        av = ((self.t[P] + self.va.loc[P, "B1G"]).to_numpy()) / x
        return P, Ad, Am, av

    def leontief(self) -> pd.DataFrame:
        P, Ad, _, _ = self.coefficients()
        return pd.DataFrame(np.linalg.inv(np.eye(len(P)) - Ad), index=P, columns=P)

    def quantites(self, fd: pd.Series) -> pd.Series:
        """Production induite par une demande finale adressée aux produits intérieurs (M€)."""
        L = self.leontief()
        return L @ fd.reindex(L.index).fillna(0.0)

    def contenu_importe(self) -> pd.Series:
        """Importations induites, directes et indirectes, par euro de demande finale intérieure de chaque produit."""
        P, Ad, Am, _ = self.coefficients()
        L = np.linalg.inv(np.eye(len(P)) - Ad)
        return pd.Series(Am.sum(axis=0) @ L, index=P)

    def prix(self, choc_import: pd.Series | None = None, choc_va: pd.Series | None = None) -> pd.Series:
        """Indices de prix de production (base 1) après chocs relatifs sur les prix d'importation (par produit
        importé) et sur la valeur ajoutée unitaire (par branche) : p = (pm Am + pv av)(I − Ad)⁻¹."""
        P, Ad, Am, av = self.coefficients()
        pm = np.ones(len(P)) if choc_import is None else 1 + choc_import.reindex(P).fillna(0).to_numpy()
        pv = np.ones(len(P)) if choc_va is None else 1 + choc_va.reindex(P).fillna(0).to_numpy()
        cout_ext = (pm @ Am) + pv * av
        p = cout_ext @ np.linalg.inv(np.eye(len(P)) - Ad)
        return pd.Series(p, index=P)

    def prix_consommation(self, p: pd.Series, pm: pd.Series | None = None) -> float:
        """Indice des prix de la consommation finale des ménages (pondérations courantes intérieur + importé)."""
        P = p.index
        cd = self.Fd.loc[P, "P3_S14"]
        cm = self.Fm.loc[P, "P3_S14"]
        pmv = pd.Series(1.0, index=P) if pm is None else 1 + pm.reindex(P).fillna(0)
        return float(((cd * p).sum() + (cm * pmv).sum()) / (cd.sum() + cm.sum()))


def indices_prix(tables: dict, annee: int) -> pd.DataFrame:
    """Variation de prix N/N−1 par produit : production (P1 courant / P1 aux prix de N−1) et importations."""
    cour = TableES(tables, annee, "courants")
    pyp = TableES(tables, annee, "pyp")
    P = cour.actifs
    imp_cour = pd.Series([float(tables["OFFRE"].get(("P7", c, str(annee)), np.nan)) for c in P], index=P)
    imp_pyp = pd.Series([float(tables["OFFRE_PYP"].get(("P7", c, str(annee)), np.nan)) for c in P], index=P)
    # produits sans importation significative : prix d'importation non défini (NaN), traité comme inchangé
    imp_pyp = imp_pyp.where(imp_cour > 50)
    return pd.DataFrame({"prix_production": cour.x[P] / pyp.x[P] - 1, "prix_import": imp_cour / imp_pyp - 1,
                         "production_cour": cour.x[P], "import_cour": imp_cour})
