"""M4 — Population de ménages et de foyers fiscaux (lot 4, version 1).

Base : fichier détail du recensement 2022 (Insee, « Individus localisés à la région », licence ouverte),
qui contient de vrais ménages anonymisés (identifiant de ménage, lien à la personne de référence, âge, sexe,
statut conjugal, activité, groupe socioprofessionnel, temps partiel) avec un poids. On n'y invente donc
aucune structure familiale (révision de la décision A4).

Étapes :
1. Tirage aléatoire simple de ménages ordinaires (taux f) ; poids = IPONDI / f.
2. Constitution des foyers fiscaux (règles explicites, voir `constituer_foyers`).
3. Score latent de revenu par adulte, à partir de grilles publiées (Insee, DREES) ; il ne sert qu'à ORDONNER
   les foyers et à répartir les revenus entre membres.
4. Ancrage sur la distribution fiscale publiée (DGFiP, IRCOM, revenus 2024) : les foyers sont classés selon
   leur score et reçoivent le revenu fiscal de référence (RFR) correspondant à leur rang dans la distribution
   DGFiP ; les salaires et pensions déclarés sont ensuite fixés par tranche selon les rapports publiés
   (salaires / RFR, pensions / RFR) et répartis entre membres selon leur score.
L'impôt net par tranche n'est PAS utilisé : il sert de test (comparaison avec OpenFisca).
"""
from __future__ import annotations

import io
import pathlib
import sys
import zipfile

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from telechargement import telecharger  # noqa: E402

URL_RP = "https://www.insee.fr/fr/statistiques/fichier/8590183/RP2022_indreg.parquet"
URL_IRCOM = ("https://static.data.gouv.fr/resources/limpot-sur-le-revenu-par-collectivite-territoriale-ircom/"
             "20260526-131537/ircom-2025-revenus-2024.zip")
COLS = ["REGION", "NUMMR", "AGEREV", "SEXE", "LPRM", "NUMF", "LIENF", "STAT_CONJ", "TACT", "TP", "STAT", "GS",
        "ETUD", "IPONDI", "CATPC", "ILT", "STOCD", "SURF", "DEPT"]

# --- Grilles publiées servant au score latent ------------------------------------------------------
# Salaire mensuel net moyen en EQTP, secteur privé, 2024 (Insee, base Tous salariés) : cadres F/H 4 180 / 4 906,
# professions intermédiaires 2 468 / 2 780, employés 1 940, ouvriers 2 050 (écart F/H global 13 %).
SAL_EQTP = {("3", "2"): 4180, ("3", "1"): 4906, ("4", "2"): 2468, ("4", "1"): 2780,
            ("5", "2"): 1900, ("5", "1"): 2000, ("6", "2"): 1800, ("6", "1"): 2100}
SIGMA_SAL = {"3": 0.45, "4": 0.30, "5": 0.25, "6": 0.25}
# Pension brute moyenne de droit direct fin 2023 (DREES) : femmes 1 306 €, hommes 2 089 € ; avec réversion 1 580 / 2 118.
PENSION = {"2": 1306, "1": 2089}
REVERSION_VEUVE = 1580 - 1306


def charger_ircom() -> pd.DataFrame:
    """Distribution nationale des foyers par tranche de RFR (IRCOM 2025, revenus 2024), montants en euros."""
    p = telecharger(URL_IRCOM, "dgfip_ircom_2025_rev2024.zip")
    raw = pd.read_excel(io.BytesIO(zipfile.ZipFile(p).read("ircom_2025_revenus_2024/national/national.xls")), header=None)
    lignes = []
    for _, r in raw.iterrows():
        lib = str(r[1])
        if not any(c.isdigit() for c in lib) or "dont" in lib.lower() or lib.startswith("Plus de 100 000"):
            continue
        if "Plus de 9" in lib:
            bas, haut = 9_000_000, np.inf
        else:
            a, b = lib.replace(" ", "").split("à")
            bas, haut = float(a) - (1 if a != "0" else 0), float(b)
        num = lambda x: float(x) if str(x) not in ("n.c.", "nan") else np.nan  # noqa: E731
        lignes.append({"tranche": lib.strip(), "bas": max(bas, 0.0), "haut": haut, "foyers": num(r[2]),
                       "rfr": num(r[3]) * 1e3, "impot": num(r[4]) * 1e3, "foyers_imposes": num(r[5]),
                       "foyers_sal": num(r[7]), "salaires": num(r[8]) * 1e3,
                       "foyers_pen": num(r[9]), "pensions": num(r[10]) * 1e3})
    return pd.DataFrame(lignes)


def echantillon_menages(f: float, graine: int = 2026) -> pd.DataFrame:
    """Tire une fraction f des ménages ordinaires et renvoie tous leurs membres."""
    p = telecharger(URL_RP, "insee_rp2022_indreg.parquet")
    t = pq.read_table(p, columns=["REGION", "NUMMR", "CATPC"])
    t = t.filter(pc.equal(t["CATPC"], "0"))
    cle = pc.binary_join_element_wise(t["REGION"], t["NUMMR"], "_")
    uniq = pc.unique(cle).to_numpy(zero_copy_only=False)
    rng = np.random.default_rng(graine)
    choisis = uniq[rng.random(len(uniq)) < f]
    del t, cle
    morceaux = []
    pf = pq.ParquetFile(p)
    sel = set(choisis.tolist())
    for i in range(pf.num_row_groups):
        rg = pf.read_row_group(i, columns=COLS)
        k = pc.binary_join_element_wise(rg["REGION"], rg["NUMMR"], "_")
        masque = pc.is_in(k, value_set=__import__("pyarrow").array(list(sel)))
        morceaux.append(rg.filter(masque).to_pandas())
    df = pd.concat(morceaux, ignore_index=True)
    df = df[df.CATPC == "0"].copy()
    df["men"] = df.REGION + "_" + df.NUMMR
    df["age"] = df.AGEREV.astype(int)
    df["poids"] = df.IPONDI / f
    df.attrs["n_menages_univers"] = len(uniq)
    return df.drop(columns=["AGEREV", "IPONDI", "CATPC"])


def constituer_foyers(df: pd.DataFrame) -> pd.DataFrame:
    """Règles (version 1) :
    - les membres adultes d'une même famille (NUMF) mariés ou pacsés (STAT_CONJ 1 ou 2) forment un foyer commun ;
      les concubins déclarent séparément ;
    - un enfant de famille (LIENF = 3) est rattaché au foyer de sa famille s'il a moins de 18 ans, ou moins de 25 ans
      et poursuit des études ; il est rattaché au premier adulte de la famille (pour les concubins : le plus âgé) ;
    - toute autre personne forme son propre foyer.
    Renvoie df avec les colonnes foyer, role (dec, conj, pac)."""
    df = df.sort_values(["men", "NUMF", "LIENF", "age"], ascending=[True, True, True, False]).copy()
    df["foyer"] = df["men"] + "_" + df.index.astype(str)
    df["role"] = "dec"
    est_adulte_fam = df.LIENF.isin(["1", "2"]) & (df.NUMF != "Z")
    marie = df.STAT_CONJ.isin(["1", "2"])
    fam = df.men + "_F" + df.NUMF
    # adultes de famille : premier adulte (le plus âgé) = déclarant
    adultes = df[est_adulte_fam]
    premier = adultes.groupby(fam[est_adulte_fam]).head(1)
    tete = pd.Series(premier.foyer.values, index=fam[premier.index].values)
    nb_maries = adultes[marie[est_adulte_fam]].groupby(fam[est_adulte_fam & marie]).size()
    couple_fiscal = nb_maries[nb_maries >= 2].index
    second = adultes.drop(premier.index)
    idx_conj = second.index[fam[second.index].isin(couple_fiscal) & marie[second.index]]
    df.loc[idx_conj, "foyer"] = tete.reindex(fam[idx_conj]).values
    df.loc[idx_conj, "role"] = "conj"
    enf = (df.LIENF == "3") & (df.NUMF != "Z") & ((df.age < 18) | ((df.age < 25) & (df.ETUD == "1")))
    cible = tete.reindex(fam[enf]).values
    ok = pd.notna(cible)
    idx = df.index[enf][ok]
    df.loc[idx, "foyer"] = cible[ok]
    df.loc[idx, "role"] = "pac"
    return df


def score_latent(df: pd.DataFrame, graine: int = 7) -> pd.Series:
    """Revenu annuel latent (euros) par personne ; sert d'ordre et de clé de répartition, pas de niveau."""
    rng = np.random.default_rng(graine)
    n = len(df)
    s = np.zeros(n)
    z = rng.standard_normal(n)
    age_prof = np.interp(df.age, [16, 22, 30, 40, 50, 60, 70], [0.55, 0.70, 0.90, 1.02, 1.10, 1.12, 1.10])
    occ = (df.TACT == "11").to_numpy()
    sal = occ & (df.STAT == "10").to_numpy()
    base = np.array([SAL_EQTP.get((g, x), 2200) for g, x in zip(df.GS, df.SEXE)]) * 12
    sig = np.array([SIGMA_SAL.get(g, 0.35) for g in df.GS])
    tp = np.where(df.TP.to_numpy() == "2", 0.6, 1.0)
    s[sal] = (base * age_prof * tp * np.exp(sig * z - sig ** 2 / 2))[sal]
    indep = occ & ~sal
    s[indep] = (32_000 * np.exp(0.9 * z - 0.405))[indep]
    chom = (df.TACT == "12").to_numpy()
    s[chom] = (13_000 * np.exp(0.5 * z - 0.125))[chom]
    ret = (df.TACT == "21").to_numpy()
    pen = np.array([PENSION[x] for x in df.SEXE]) * 12 + np.where(df.STAT_CONJ.to_numpy() == "4", REVERSION_VEUVE * 12, 0)
    s[ret] = (pen * np.exp(0.5 * z - 0.125))[ret]
    autres = (~occ & ~chom & ~ret & (df.age >= 18)).to_numpy()
    s[autres] = (3_000 * np.exp(1.0 * z - 0.5))[autres]
    return pd.Series(s, index=df.index)


def quantile_rfr(ircom: pd.DataFrame, u: np.ndarray) -> np.ndarray:
    """RFR au rang u ∈ [0,1] de la distribution DGFiP. Dans chaque tranche, densité linéaire dont la pente reproduit
    le RFR moyen publié ; dernière tranche : Pareto ajustée sur la moyenne."""
    t = ircom.copy()
    t["cum"] = t.foyers.cumsum() / t.foyers.sum()
    t["cum0"] = t.cum - t.foyers / t.foyers.sum()
    out = np.empty_like(u)
    for _, r in t.iterrows():
        m = (u >= r.cum0) & (u < r.cum) if np.isfinite(r.haut) else (u >= r.cum0)
        if not m.any():
            continue
        v = (u[m] - r.cum0) / (r.cum - r.cum0)
        moy = r.rfr / r.foyers
        if np.isfinite(r.haut):
            a, b = r.bas, r.haut
            # densité f(x) = (1 + c·(x − mil)) / (b − a) ; c choisi pour la moyenne (borné pour rester positive)
            mil, L = (a + b) / 2, b - a
            c = np.clip(12 * (moy - mil) / L ** 2, -2 / L * 0.999, 2 / L * 0.999)
            # inversion de la fonction de répartition F(x) = (x−a)/L + c/(2L)·((x−mil)² − (L/2)²)
            if abs(c) < 1e-12:
                out[m] = a + v * L
            else:
                # en y = x − mil : F(y) = (y + L/2)/L + c/(2L)(y² − L²/4) = v  →  A y² + B y + C = 0
                A, B = c / (2 * L), 1 / L
                C = 0.5 - c * L / 8 - v
                y = (-B + np.sqrt(np.maximum(B * B - 4 * A * C, 0))) / (2 * A)
                out[m] = mil + y
        else:
            alpha = moy / (moy - r.bas)
            out[m] = r.bas * (1 - v) ** (-1 / alpha)
    return out


def construire(f: float = 0.02, graine: int = 2026) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Renvoie (individus, foyers, ircom)."""
    ircom = charger_ircom()
    ind = constituer_foyers(echantillon_menages(f, graine))
    ind["score"] = score_latent(ind)
    ret = ind.TACT == "21"
    ind["score_sal"] = np.where(ret, 0.0, ind.score)
    ind["score_pen"] = np.where(ret, ind.score, 0.0)
    fo = ind.groupby("foyer").agg(poids=("poids", "first"), score=("score", "sum"),
                                  score_sal=("score_sal", "sum"), score_pen=("score_pen", "sum"),
                                  n=("age", "size"), n_pac=("role", lambda r: (r == "pac").sum()),
                                  couple=("role", lambda r: (r == "conj").any()))
    indep = ind[(ind.TACT == "11") & ind.STAT.isin(["21", "22"])].foyer.unique()
    fo["independant"] = fo.index.isin(indep)
    # rang pondéré (ex aequo départagés aléatoirement), puis RFR DGFiP
    rng = np.random.default_rng(graine + 1)
    ordre = np.lexsort((rng.random(len(fo)), fo.score.to_numpy()))
    w = fo.poids.to_numpy()[ordre]
    u = np.empty(len(fo))
    u[ordre] = (np.cumsum(w) - w / 2) / w.sum()
    fo["rfr"] = quantile_rfr(ircom, u)
    fo["tranche"] = pd.cut(fo.rfr, bins=[-1] + list(ircom.haut.replace(np.inf, 1e12)), labels=ircom.tranche).astype(str)
    # salaires et pensions déclarés : rapports publiés par tranche, répartis entre salaires et pensions selon les scores
    t = ircom.set_index("tranche")
    k_sal = (t.salaires / t.rfr).reindex(fo.tranche).to_numpy()
    k_pen = (t.pensions / t.rfr).reindex(fo.tranche).to_numpy()
    part_sal = np.where(fo.score > 0, fo.score_sal / fo.score.replace(0, 1), 0.5)
    # niveau total déclaré = RFR × (k_sal + k_pen) ; partage selon la composition du foyer
    tot = fo.rfr.to_numpy() * (k_sal + k_pen)
    fo["salaires"] = tot * part_sal
    fo["pensions"] = tot * (1 - part_sal)
    # calage des montants MOYENS par foyer de chaque tranche sur la DGFiP (corrige l'effet de composition du
    # partage) ; on cale les moyennes et non les masses, car la base couvre moins de foyers que la DGFiP
    # (communautés exclues du champ des ménages ordinaires, règles de rattachement simplifiées)
    n_simul = fo.poids.groupby(fo.tranche).sum()
    for col in ("salaires", "pensions"):
        cible = t[col] / t.foyers * n_simul.reindex(t.index)
        simul = (fo[col] * fo.poids).groupby(fo.tranche).sum()
        fo[col] *= (cible / simul.replace(0, np.nan)).reindex(fo.tranche).fillna(1).to_numpy()
    # répartition aux individus au prorata des scores
    for col, sc in (("salaires", "score_sal"), ("pensions", "score_pen")):
        tot_sc = ind.groupby("foyer")[sc].transform("sum")
        ind[col] = np.where(tot_sc > 0, ind[sc] / tot_sc.replace(0, 1), 0) * fo[col].reindex(ind.foyer).to_numpy()
        # foyers sans score correspondant : montant au déclarant
        manque = (tot_sc == 0) & (ind.role == "dec")
        ind.loc[manque, col] = fo[col].reindex(ind.foyer[manque]).to_numpy()
    return ind, fo, ircom


# ---------------------------------------------------------------------------------------------------
# Version 1.1 : décomposition des autres revenus et dépenses ouvrant droit à crédits ou réductions
# ---------------------------------------------------------------------------------------------------
URL_CASES = ("https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/ir-declarations-2042-nat/"
             "exports/csv?delimiter=%3B")


def totaux_cases(annee: int = 2024) -> dict:
    """Masses nationales (euros) par catégorie, d'après les déclarations nationales DGFiP (revenus de l'année)."""
    d = pd.read_csv(telecharger(URL_CASES, "dgfip_ir_declarations_2042_nat.csv"), sep=";")
    d = d[d.annee.astype(str).str[:4] == str(annee)].set_index("nom")
    m = lambda codes: float(d.montant.reindex(codes).fillna(0).sum())  # noqa: E731
    n = lambda codes: float(d.nombre.reindex(codes).fillna(0).max())  # noqa: E731
    cinq = d[d.index.str.startswith("5")]
    # bénéfices et revenus imposables des indépendants (hors micro-entrepreneurs au versement libératoire), moins déficits
    pro_pos = cinq[cinq.libelle.str.contains("énéfices|Revenus imposables|revenus imposables", regex=True)
                   & ~cinq.libelle.str.contains("Micro-entrepreneur")].montant.sum()
    pro_neg = cinq[cinq.libelle.str.contains("éficit")].montant.sum()
    meubles_micro = m(["5ND", "5OD", "5KP", "5LP", "5KO", "5LO"])  # recettes micro : abattement moyen ≈ 50 %
    return {
        "hs_exonerees": m(["1GH", "1HH", "1IH", "1JH"]), "foyers_hs": n(["1GH"]),
        "dividendes": m(["2DC"]), "interets": m(["2TR", "2TS"]), "plus_values": m(["3VG"]) - m(["3VH"]),
        "foncier": m(["4BA"]) - m(["4BC"]) + 0.7 * m(["4BE"]),
        "independants": pro_pos - pro_neg + 0.5 * meubles_micro,
        "emploi_domicile": m(["7DB"]), "foyers_emploi_domicile": n(["7DB"]),
        "garde": m(["7GA", "7GB", "7GC"]), "foyers_garde": n(["7GA"]),
        "dons_oeuvres": m(["7UF"]), "foyers_dons_oeuvres": n(["7UF"]),
        "dons_difficulte": m(["7UD"]), "foyers_dons_difficulte": n(["7UD"]),
        "salaires_etrangers_ci": m(["1AF", "1BF", "1CF"]),
        "epargne_retraite": m(["6NS", "6NT", "6RS", "6RT", "6QS", "6QT"]), "personnes_epargne_retraite": n(["6NS"]) + n(["6NT"]) + n(["6RS"]),
    }


def imputer_heures_sup(ind: pd.DataFrame, total: float, plafond: float = 7_500) -> pd.Series:
    """Heures supplémentaires exonérées (incluses dans les salaires de l'IRCOM) : salariés hors cadres (poids 1) et
    cadres (poids 0,4), proportionnelles au salaire, plafonnées par la loi (7 500 €) et à 25 % du salaire."""
    sal = ind.salaires.to_numpy()
    w = np.where(ind.STAT == "10", np.where(ind.GS == "3", 0.4, 1.0), 0.0) * (sal > 0)
    cap = np.minimum(plafond, 0.25 * sal)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        tau = (lo + hi) / 2
        tot = (ind.poids.to_numpy() * np.minimum(tau * w * sal, cap)).sum()
        lo, hi = (tau, hi) if tot < total else (lo, tau)
    return pd.Series(np.minimum(tau * w * sal, cap), index=ind.index)


def repartir_autres(fo: pd.DataFrame, reste: pd.Series, totaux: dict, eta_capital: float = 0.8,
                    eta_bareme: float = 0.2, bonus_independant: float = 5.0) -> pd.DataFrame:
    """Répartit le reste de chaque foyer entre revenus du capital (PFU : dividendes, intérêts, plus-values), revenus au
    barème (fonciers, indépendants) et un poste « exonere » : part du reste qui dépasse les masses nationales par case
    (revenus inclus dans le RFR mais non imposés au barème : revenus étrangers à crédit égal à l'impôt français hors
    frontaliers, plus-values en report, revenus exonérés, abattements réintégrés…).
    Ajustement biproportionnel par tranche (RAS) : lignes = masse du reste par tranche, colonnes = masses nationales
    (non remises à l'échelle) ; a priori ∝ masse × (RFR moyen de la tranche)^η ; le poste exonéré suit le profil du
    capital. Les foyers comptant un indépendant reçoivent une part au barème renforcée. η et bonus : niveau D."""
    cats = ["dividendes", "interets", "plus_values", "foncier", "independants", "exonere"]
    eta = {"dividendes": eta_capital, "interets": eta_capital, "plus_values": eta_capital,
           "foncier": eta_bareme, "independants": eta_bareme, "exonere": eta_capital}
    w = fo.poids
    R_b = (reste * w).groupby(fo.tranche).sum()
    m_b = (fo.rfr * w).groupby(fo.tranche).sum() / w.groupby(fo.tranche).sum()
    couverts = sum(totaux[c] for c in cats[:-1])
    T = pd.Series({c: totaux[c] for c in cats[:-1]})
    T = T * min(1.0, R_b.sum() / couverts)
    T["exonere"] = max(0.0, R_b.sum() - T.sum())
    P = pd.DataFrame({c: max(T[c], 1.0) * (m_b / m_b.median()) ** eta[c] for c in cats})
    P = P.div(P.sum(axis=1), axis=0).mul(R_b, axis=0)
    for _ in range(300):  # RAS
        P = P.mul(T.clip(lower=1e-9) / P.sum().clip(lower=1e-9), axis=1)
        P = P.mul(R_b / P.sum(axis=1).clip(lower=1e-9), axis=0)
    parts = P.div(P.sum(axis=1), axis=0).fillna(0)
    a = parts.reindex(fo.tranche).to_numpy()
    bonus = np.where(fo.independant.to_numpy()[:, None], np.array([1, 1, 1, 1, bonus_independant, 1]), 1.0)
    a = a * bonus
    a = a / a.sum(axis=1, keepdims=True).clip(min=1e-12)
    out = pd.DataFrame(a * reste.to_numpy()[:, None], index=fo.index, columns=cats).fillna(0)
    out.attrs["facteur_masses"] = float(R_b.sum() / couverts)
    out.attrs["part_exoneree"] = float(T["exonere"] / R_b.sum())
    return out


def lire_deciles_dgfip(annee: int = 2024) -> pd.DataFrame:
    """Tableau DGFiP « répartition de l'impôt moyen par déciles de RFR par part » (impots.gouv.fr, node 25518), en euros
    par part : parts moyennes, RFR, impôt au barème, impôt forfaitaire, CEHR, réductions et crédits (RICI), IR net."""
    import openpyxl
    p = telecharger("https://www.impots.gouv.fr/node/25518", "dgfip_ir_deciles_rfr_part.xlsx")
    ws = openpyxl.load_workbook(p, data_only=True)[f"a{annee}"]
    lignes = []
    for r in ws.iter_rows(values_only=True):
        if r[0] is not None and str(r[0]).strip().isdigit():
            v = [x for x in r[1:] if isinstance(x, (int, float))]
            d = int(str(r[0]).strip())
            # bornes présentes : une seule pour les déciles 1 et 10, deux sinon ; taux « n.s. » possibles au décile 1
            v = v[(1 if d in (1, 10) else 2):]
            v = (v + [np.nan] * 9)[:9]
            lignes.append(dict(zip(["parts", "rfr", "bareme", "forfaitaire", "cehr", "rici", "net", "taux_av", "taux_ap"],
                                   [v[0], v[1] * 1e3, v[2] * 1e3, v[3] * 1e3, v[4] * 1e3, v[5] * 1e3, v[6] * 1e3, v[7], v[8]]),
                               decile=d))
    return pd.DataFrame(lignes).set_index("decile")


def deciles_rfr_par_part(fo: pd.DataFrame, nbptr: pd.Series) -> pd.Series:
    """Décile (1-10) de RFR par part, pondéré."""
    rpp = (fo.rfr / nbptr.clip(lower=0.5)).to_numpy()
    o = np.argsort(rpp, kind="stable")
    cw = np.cumsum(fo.poids.to_numpy()[o]) / fo.poids.sum()
    d = np.empty(len(fo), dtype=int)
    d[o] = np.minimum((cw * 10).astype(int) + 1, 10)
    return pd.Series(d, index=fo.index)


def caler_rici_residuelles(fo: pd.DataFrame, impot_avant: pd.Series, rici_modele: pd.Series, nbptr: pd.Series,
                           deciles: pd.Series, dgfip: pd.DataFrame) -> pd.Series:
    """Réductions et crédits non modélisés un à un (investissements locatifs, souscriptions PME, outre-mer, dépendance…) :
    l'écart par décile entre les RICI de la DGFiP et ceux du modèle est réparti au prorata de l'impôt avant RICI du
    foyer, sans dépasser cet impôt. Renvoie le montant résiduel par foyer (à soustraire de l'impôt)."""
    w = fo.poids
    out = pd.Series(0.0, index=fo.index)
    for d in range(1, 11):
        m = deciles == d
        cible = dgfip.loc[d, "rici"] * (nbptr[m] * w[m]).sum()
        ecart = cible - (rici_modele[m] * w[m]).sum()
        base = impot_avant[m].clip(lower=0)
        if ecart > 0 and (base * w[m]).sum() > 0:
            out[m] = np.minimum(base, base * ecart / (base * w[m]).sum())
    return out


def imputer_depenses(fo: pd.DataFrame, ind: pd.DataFrame, totaux: dict, couverture: float, graine: int = 11) -> pd.DataFrame:
    """Dépenses ouvrant droit à crédit ou réduction, imputées pour reproduire les nombres de foyers et montants
    nationaux (ramenés à la couverture de la population). Probabilités croissantes avec le rang de revenu ;
    emploi à domicile renforcé à partir de 75 ans ; garde réservée aux foyers ayant un enfant de moins de 6 ans."""
    rng = np.random.default_rng(graine)
    w = fo.poids.to_numpy()
    r = fo.rfr.rank(pct=True).to_numpy()
    u = rng.random((4, len(fo)))
    age_dec = ind[ind.role == "dec"].groupby("foyer").age.first().reindex(fo.index).to_numpy()
    jeunes = ind[(ind.role == "pac") & (ind.age < 6)].groupby("foyer").size().reindex(fo.index).fillna(0).to_numpy()

    def tirer(score, n_cible, montant, k_u, mult=None):
        lo, hi = 0.0, 50.0
        for _ in range(60):
            c = (lo + hi) / 2
            p = np.minimum(1, c * score)
            lo, hi = (c, hi) if (w * p).sum() < n_cible else (lo, c)
        sel = u[k_u] < np.minimum(1, c * score)
        base = np.where(sel, (mult if mult is not None else 1.0) * (0.5 + r), 0.0)
        return base * montant / max((w * base).sum(), 1e-9)

    out = pd.DataFrame(index=fo.index)
    out["f7db"] = tirer(r ** 1.5 * np.where(age_dec >= 75, 3.0, 1.0), totaux["foyers_emploi_domicile"] * couverture,
                        totaux["emploi_domicile"] * couverture, 0)
    out["f7ga"] = tirer((jeunes > 0) * (0.3 + r), totaux["foyers_garde"] * couverture, totaux["garde"] * couverture, 1)
    out["f7ga"] = np.minimum(out.f7ga, 3_500)  # plafond par enfant (le crédit de 50 % est calculé par OpenFisca)
    out["f7uf"] = tirer(r ** 2, totaux["foyers_dons_oeuvres"] * couverture, totaux["dons_oeuvres"] * couverture, 2)
    out["f7ud"] = tirer(r ** 1.5, totaux["foyers_dons_difficulte"] * couverture, totaux["dons_difficulte"] * couverture, 3)
    return out


def imputer_epargne_retraite(ind: pd.DataFrame, fo: pd.DataFrame, total: float, n_cible: float, graine: int = 13) -> pd.Series:
    """Versements déductibles d'épargne retraite (cases 6NS, 6RS, 6QS…) : actifs occupés de 30 à 64 ans, probabilité
    croissante avec le rang du foyer, montant proportionnel au RFR du foyer et plafonné à 10 % des revenus d'activité
    (plafond légal simplifié). Déduits du revenu imposable, réintégrés dans le RFR."""
    rng = np.random.default_rng(graine)
    r = fo.rfr.rank(pct=True).reindex(ind.foyer).to_numpy()
    elig = ((ind.TACT == "11") & ind.age.between(30, 64)).to_numpy()
    score = elig * r ** 2.5
    w = ind.poids.to_numpy()
    u = rng.random(len(ind))
    lo, hi = 0.0, 50.0
    for _ in range(60):
        c = (lo + hi) / 2
        lo, hi = (c, hi) if (w * np.minimum(1, c * score)).sum() < n_cible else (lo, c)
    sel = u < np.minimum(1, c * score)
    plafond = 0.10 * (ind.salaires.to_numpy() + 0)
    rfr_f = fo.rfr.reindex(ind.foyer).to_numpy()
    base = np.where(sel, rfr_f, 0.0)
    k = total / max((w * base).sum(), 1e-9)
    for _ in range(20):  # mise à l'échelle sous plafond
        v = np.minimum(k * base, np.maximum(plafond, 4_637))  # plancher légal de déductibilité (10 % du PASS)
        k *= total / max((w * v).sum(), 1e-9)
    return pd.Series(np.where(sel, np.minimum(k * base, np.maximum(plafond, 4_637)), 0.0), index=ind.index)


def recaler_capital_deciles(fo: pd.DataFrame, autres: pd.DataFrame, deciles: pd.Series, dgfip: pd.DataFrame,
                            taux_pfu: float = 0.128, masse_bareme: float | None = None) -> pd.DataFrame:
    """Version 1.3 : contrainte directe sur le capital au prélèvement forfaitaire unique (PFU), par décile de RFR par part.
    La DGFiP publie le PFU moyen par part et par décile ; la masse de capital visée vaut PFU / 12,8 %. Dans chaque décile,
    le capital (dividendes, intérêts, plus-values) est remis à l'échelle ; la différence est prise sur (ou rendue à) les
    revenus au barème et le poste exonéré, au prorata de leurs montants, de sorte que le reste de chaque foyer est
    inchangé. Si `masse_bareme` est fourni, les revenus au barème sont ensuite recalés sur cette masse nationale
    déclarée, le solde allant au poste exonéré. `fo` doit contenir `nbptr` (parts OpenFisca)."""
    cap = ["dividendes", "interets", "plus_values"]
    aut = ["foncier", "independants", "exonere"]
    out = autres.copy()
    w = fo.poids
    for d in range(1, 11):
        m = (deciles == d).to_numpy()
        cible = dgfip.loc[d, "forfaitaire"] / taux_pfu * (fo.nbptr[m] * w[m]).sum()
        c_tot = out.loc[m, cap].sum(axis=1)
        a_tot = out.loc[m, aut].sum(axis=1)
        actuel = (c_tot * w[m]).sum()
        if actuel <= 0:
            continue
        f = cible / actuel
        if f > 1:  # on prend sur les autres postes, sans dépasser ce qu'ils contiennent
            besoin = (f - 1) * c_tot
            dispo = a_tot
            # facteur commun g tel que Σ w·min(g·besoin, dispo) = (f−1)·actuel
            lo, hi = 0.0, 1.0
            for _ in range(50):
                g = (lo + hi) / 2
                lo, hi = (g, hi) if (w[m] * np.minimum(g * besoin, dispo)).sum() < (f - 1) * actuel else (lo, g)
            transfert = np.minimum(g * besoin, dispo)
        else:
            transfert = (f - 1) * c_tot  # négatif : le capital rend une partie aux autres postes
        k_cap = np.where(c_tot > 0, 1 + transfert / c_tot.replace(0, 1), 1.0)
        out.loc[m, cap] = out.loc[m, cap].mul(k_cap, axis=0)
        part_aut = out.loc[m, aut].div(a_tot.replace(0, np.nan), axis=0).fillna(1 / 3)
        out.loc[m, aut] = out.loc[m, aut].sub(part_aut.mul(transfert, axis=0))
    out[aut] = out[aut].clip(lower=0)
    if masse_bareme is not None:
        # le non-capital de chaque foyer est partagé entre barème et exonéré ; un facteur commun φ sur la part au
        # barème (plafonnée à 1) rétablit la masse nationale déclarée des revenus fonciers et d'indépendants
        nc = out[aut].sum(axis=1)
        bar = out[["foncier", "independants"]].sum(axis=1)
        s0 = np.where(nc > 0, bar / nc.replace(0, 1), 0.0)
        cle_f = np.where(bar > 0, out.foncier / bar.replace(0, 1), 0.5)
        lo, hi = 0.0, 50.0
        for _ in range(60):
            phi = (lo + hi) / 2
            lo, hi = (phi, hi) if (w * nc * np.minimum(1, phi * s0)).sum() < masse_bareme else (lo, phi)
        nb = nc * np.minimum(1, phi * s0)
        out["foncier"] = nb * cle_f
        out["independants"] = nb * (1 - cle_f)
        out["exonere"] = nc - nb
    return out
