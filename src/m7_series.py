"""Lot 7 — Séries longues pour l'estimation des équations de comportement (1995-2025, annuelles).

Panel de branches marchandes (comptes nationaux annuels, Eurostat, base 2020, publiés par l'Insee) :
  q    valeur ajoutée en volume (B1G, M€ chaînés 2015)        pva  prix de la valeur ajoutée (B1G courant / volume)
  y    production en volume (P1)                               py   prix de la production
  h    heures travaillées, emploi total (milliers d'heures)    hs   heures des salariés
  n    emploi total (personnes)                                ns   salariés
  wb   rémunérations des salariés (D1)                         cs   coût horaire d'un salarié = D1 / heures salariées
  clu  coût salarial unitaire, non-salariés imputés au coût salarié horaire : cs · h / q
  i    FBCF en volume (P51G)                                   pi   prix de la FBCF
  k    stock de capital fixe net en volume (N11N)
  pm   part des profits = 1 − cs · h / B1G courant (non-salariés rémunérés comme les salariés)
Séries macroéconomiques : PIB et emplois en volume et en valeur (France, UE, zone euro), chômage BIT (Insee, France
métropolitaine), taux longs (Eurostat), compte des ménages, compte des sociétés non financières, bilans d'énergie.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from telechargement import jsonstat_dict, telecharger  # noqa: E402

B = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
# Branches marchandes retenues pour l'estimation (regroupement A38 publié, ≈ 25 branches) ; immobilier (loyers imputés)
# et branches non marchandes (O-Q) sont exclus : leur production n'obéit pas aux mêmes comportements.
BRANCHES = ["A", "B", "C10-C12", "C13-C15", "C16-C18", "C19", "C20", "C21", "C22_C23", "C24_C25", "C26", "C27", "C28",
            "C29_C30", "C31-C33", "D", "E", "F", "G", "H", "I", "J", "K", "M_N", "R-U"]
INDUSTRIE = ["B", "C10-C12", "C13-C15", "C16-C18", "C19", "C20", "C21", "C22_C23", "C24_C25", "C26", "C27", "C28",
             "C29_C30", "C31-C33", "D", "E"]
# Correspondance branches → produits A64 du bloc entrées-sorties
VERS_A64 = {"A": ["CPA_A01", "CPA_A02", "CPA_A03"], "B": ["CPA_B"], "C10-C12": ["CPA_C10-12"], "C13-C15": ["CPA_C13-15"],
            "C16-C18": ["CPA_C16", "CPA_C17", "CPA_C18"], "C19": ["CPA_C19"], "C20": ["CPA_C20"], "C21": ["CPA_C21"],
            "C22_C23": ["CPA_C22", "CPA_C23"], "C24_C25": ["CPA_C24", "CPA_C25"], "C26": ["CPA_C26"], "C27": ["CPA_C27"],
            "C28": ["CPA_C28"], "C29_C30": ["CPA_C29", "CPA_C30"], "C31-C33": ["CPA_C31_32", "CPA_C33"], "D": ["CPA_D"],
            "E": ["CPA_E36", "CPA_E37-39"], "F": ["CPA_F"], "G": ["CPA_G45", "CPA_G46", "CPA_G47"],
            "H": ["CPA_H49", "CPA_H50", "CPA_H51", "CPA_H52", "CPA_H53"], "I": ["CPA_I"],
            "J": ["CPA_J58", "CPA_J59_60", "CPA_J61", "CPA_J62_63"], "K": ["CPA_K64", "CPA_K65", "CPA_K66"],
            "M_N": ["CPA_M69_70", "CPA_M71", "CPA_M72", "CPA_M73", "CPA_M74_75", "CPA_N77", "CPA_N78", "CPA_N79", "CPA_N80-82"],
            "R-U": ["CPA_R90-92", "CPA_R93", "CPA_S94", "CPA_S95", "CPA_S96", "CPA_T", "CPA_U"]}


def _es(nom: str, requete: str) -> pd.Series:
    d = json.loads(telecharger(B + requete, nom).read_text(encoding="utf-8"))
    return pd.Series(jsonstat_dict(d))


def bdm(idbank: str) -> pd.Series:
    """Série de la Banque de données macroéconomiques de l'Insee (SDMX, sans clé d'accès)."""
    t = telecharger(f"https://www.bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbank}", f"insee_bdm_{idbank}.xml").read_text()
    obs = re.findall(r'TIME_PERIOD="([^"]+)" OBS_VALUE="([^"]+)"', t)
    return pd.Series({p: float(v) for p, v in obs}).sort_index()


def panel_branches() -> pd.DataFrame:
    a = _es("eurostat_nama_10_a64_FR.json", "nama_10_a64?format=JSON&geo=FR&sinceTimePeriod=1995&na_item=B1G&na_item=P1&na_item=D1&na_item=D11&unit=CP_MEUR&unit=CLV15_MEUR&unit=PYP_MEUR")
    e = _es("eurostat_nama_10_a64_e_FR.json", "nama_10_a64_e?format=JSON&geo=FR&sinceTimePeriod=1995&na_item=EMP_DC&na_item=SAL_DC&unit=THS_PER&unit=THS_HW")
    f = _es("eurostat_nama_10_a64_p5_FR.json", "nama_10_a64_p5?format=JSON&geo=FR&sinceTimePeriod=1995&asset10=N11G&unit=CP_MEUR&unit=CLV15_MEUR")
    k = _es("eurostat_nama_10_nfa_st_FR.json", "nama_10_nfa_st?format=JSON&geo=FR&sinceTimePeriod=1995&asset10=N11N&unit=CP_MEUR&unit=CLV15_MEUR")
    lignes = []
    for b in BRANCHES:
        for t in range(1995, 2026):
            y = str(t)
            g = lambda s, *cle: float(s.get(cle, np.nan))  # noqa: E731
            r = dict(branche=b, annee=t,
                     va_cp=g(a, "CP_MEUR", b, "B1G", y), q=g(a, "CLV15_MEUR", b, "B1G", y), va_pyp=g(a, "PYP_MEUR", b, "B1G", y),
                     y_cp=g(a, "CP_MEUR", b, "P1", y), y=g(a, "CLV15_MEUR", b, "P1", y),
                     wb=g(a, "CP_MEUR", b, "D1", y), ws=g(a, "CP_MEUR", b, "D11", y),
                     h=g(e, "THS_HW", b, "EMP_DC", y), hs=g(e, "THS_HW", b, "SAL_DC", y),
                     n=g(e, "THS_PER", b, "EMP_DC", y), ns=g(e, "THS_PER", b, "SAL_DC", y),
                     i_cp=g(f, "CP_MEUR", b, "P51G", y), i=g(f, "CLV15_MEUR", b, "P51G", y),
                     k=g(k, b, y))
            lignes.append(r)
    p = pd.DataFrame(lignes)
    p["pva"] = p.va_cp / p.q
    p["py"] = p.y_cp / p.y
    p["pi"] = p.i_cp / p.i
    p["cs"] = p.wb / p.hs                      # coût horaire salarié (M€ par millier d'heures)
    p["clu"] = p.cs * p.h / p.q                # coût salarial unitaire (non-salariés imputés)
    p["part_salaires"] = p.cs * p.h / p.va_cp
    p["pm"] = 1 - p.part_salaires
    p["productivite"] = p.q / p.h
    return p


def macro() -> pd.DataFrame:
    g = _es("eurostat_nama_10_gdp_FR_EU.json", "nama_10_gdp?format=JSON&geo=FR&geo=EU27_2020&geo=EA20&unit=CLV15_MEUR&unit=CP_MEUR&na_item=B1GQ&na_item=P3_S14&na_item=P3_S13&na_item=P51G&na_item=P6&na_item=P7&na_item=P3&na_item=P5G&sinceTimePeriod=1980")
    ans = range(1980, 2026)
    d = pd.DataFrame(index=list(ans))
    for geo, pre in (("FR", ""), ("EU27_2020", "ue_"), ("EA20", "ze_")):
        for it, nom in (("B1GQ", "pib"), ("P3_S13", "g"), ("P51G", "fbcf"), ("P6", "x"), ("P7", "m"), ("P5G", "fbc")):
            d[pre + nom] = [float(g.get(("CLV15_MEUR", it, geo, str(t)), np.nan)) for t in ans]
            d[pre + nom + "_cp"] = [float(g.get(("CP_MEUR", it, geo, str(t)), np.nan)) for t in ans]
    for nom in ("pib", "x", "m", "fbcf", "g", "fbc", "ue_x", "ue_m", "ze_x", "ze_m"):
        d["p_" + nom] = d[nom + "_cp"] / d[nom]
    dm = demande_mondiale_adressee()
    d["dm"] = dm.indice.reindex(list(ans)).to_numpy()
    u = bdm("001688526")
    u.index = u.index.str[:4]
    d["chomage"] = u.groupby(level=0).mean().reindex([str(t) for t in ans]).to_numpy()
    r = _es("eurostat_irt_lt_mcby_a_FR.json", "irt_lt_mcby_a?format=JSON&geo=FR&geo=DE&sinceTimePeriod=1980")
    d["taux_long"] = [float(r.get(("FR", str(t)), np.nan)) for t in ans]
    h = _es("eurostat_nasa_10_nf_tr_S14_FR.json", "nasa_10_nf_tr?format=JSON&geo=FR&unit=CP_MEUR&sector=S14_S15&direct=PAID&direct=RECV&na_item=B6G&na_item=P3&na_item=B8G&na_item=D1&sinceTimePeriod=1995")
    d["rdb"] = [float(h.get(("PAID", "B6G", str(t)), h.get(("RECV", "B6G", str(t)), np.nan))) for t in ans]
    d["epargne"] = [float(h.get(("PAID", "B8G", str(t)), h.get(("RECV", "B8G", str(t)), np.nan))) for t in ans]
    fc = _es("eurostat_nama_10_fcs_FR.json", "nama_10_fcs?format=JSON&geo=FR&unit=CLV15_MEUR&unit=CP_MEUR&na_item=P31_S14&sinceTimePeriod=1980")
    d["c"] = [float(fc.get(("CLV15_MEUR", str(t)), np.nan)) for t in ans]
    d["c_cp"] = [float(fc.get(("CP_MEUR", str(t)), np.nan)) for t in ans]
    d["p_c"] = d.c_cp / d.c
    return d


def taux_is() -> pd.Series:
    """Taux normal de l'impôt sur les sociétés, contributions additionnelles comprises (grandes entreprises), en %.
    Source : législation (CGI art. 219 ; contributions de 10 % 1995-2005 puis 3,3 % ; contribution exceptionnelle 2011-2017
    pour les très grandes entreprises non retenue ; baisse progressive 2018-2022 ; contribution exceptionnelle 2025)."""
    t = {1995: 36.66, 1996: 36.66, 1997: 41.66, 1998: 41.66, 1999: 40.0, 2000: 37.76, 2001: 36.43, 2002: 35.43,
         2003: 35.43, 2004: 35.43, 2005: 34.93, 2006: 34.43, 2007: 34.43, 2008: 34.43, 2009: 34.43, 2010: 34.43,
         2011: 34.43, 2012: 34.43, 2013: 34.43, 2014: 34.43, 2015: 34.43, 2016: 34.43, 2017: 34.43, 2018: 34.43,
         2019: 32.02, 2020: 32.02, 2021: 28.41, 2022: 25.83, 2023: 25.83, 2024: 25.83, 2025: 25.83}
    return pd.Series(t, dtype=float)


def demande_mondiale_adressee() -> pd.DataFrame:
    """Demande mondiale adressée à la France (biens et services, volume) :
    croissance_t = Σ_c w_{c,t−1} · croissance des importations en volume du pays c (FMI, Perspectives de l'économie
    mondiale, avril 2025, TM_RPCH), w = part du pays c dans les exportations de biens de la France (FMI, Direction of
    Trade Statistics), via DBnomics. Couvre les pays présents dans les deux sources (≈ 98 % des exportations).
    Renvoie un indice (base 2015 = 100) et la part couverte. Limite : pondération par les exportations de biens
    seulement ; prévisions du FMI au-delà de 2024."""
    import pycountry
    dot = json.loads(telecharger("https://api.db.nomics.world/v22/series/IMF/DOT?dimensions=%7B%22REF_AREA%22:%5B%22FR%22%5D,"
                                 "%22INDICATOR%22:%5B%22TXG_FOB_USD%22%5D,%22FREQ%22:%5B%22A%22%5D%7D&observations=1&limit=1000",
                                 "dbnomics_imf_dot_fr_exports.json").read_text())
    weo = json.loads(telecharger("https://api.db.nomics.world/v22/series/IMF/WEO:2025-04?dimensions=%7B%22weo-subject%22:%5B%22TM_RPCH%22%5D%7D"
                                 "&observations=1&limit=1000", "dbnomics_imf_weo_2025_04_tm_rpch.json").read_text())
    exp = {}
    for x in dot["series"]["docs"]:
        p = x["series_code"].split(".")[-1]
        c = pycountry.countries.get(alpha_2=p)
        if c is None:
            continue
        exp[c.alpha_3] = pd.Series({int(a): (float(v) if v != "NA" else np.nan) for a, v in zip(x["period"], x["value"])})
    imp = {}
    for x in weo["series"]["docs"]:
        c = x["series_code"].split(".")[0]
        imp[c] = pd.Series({int(a): (float(v) if v != "NA" else np.nan) for a, v in zip(x["period"], x["value"])})
    E_ = pd.DataFrame(exp).loc[1980:2024]
    I_ = pd.DataFrame(imp).loc[1981:2030]
    commun = [c for c in E_.columns if c in I_.columns]
    tot = E_.sum(axis=1)
    w = E_[commun].div(tot, axis=0)
    out = {}
    for t in range(1982, 2031):
        wt = w.loc[min(t - 1, 2024)]
        g = I_.loc[t, commun]
        ok = g.notna() & wt.notna()
        out[t] = (float((wt[ok] * g[ok]).sum() / wt[ok].sum()), float(wt[ok].sum()))
    d = pd.DataFrame(out, index=["croissance", "couverture"]).T
    idx = np.exp(np.log1p(d.croissance / 100).cumsum())
    d["indice"] = idx / idx[2015] * 100
    return d


TUC_IDBANK = {"manuf": "001586739", "agro": "001586741", "equip": "001586743", "transport": "001586745", "autres": "001586747"}
TUC_BRANCHE = {"C10-C12": "agro", "C26": "equip", "C27": "equip", "C28": "equip", "C29_C30": "transport",
               "C13-C15": "autres", "C16-C18": "autres", "C20": "autres", "C21": "autres", "C22_C23": "autres",
               "C24_C25": "autres", "C31-C33": "autres", "C19": "manuf"}


def tuc() -> pd.DataFrame:
    """Taux d'utilisation des capacités de production (%, CVS, moyenne annuelle des enquêtes trimestrielles de
    conjoncture dans l'industrie, Insee), industrie manufacturière et quatre regroupements."""
    out = {}
    for k, idb in TUC_IDBANK.items():
        s = bdm(idb)
        s = s.groupby(s.index.str[:4]).mean()
        s.index = s.index.astype(int)
        out[k] = s
    return pd.DataFrame(out)
