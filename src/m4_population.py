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
        "ETUD", "IPONDI", "CATPC"]

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
