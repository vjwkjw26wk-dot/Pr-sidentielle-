"""Validation du lot 4 (population M4, version 1.3) et des masses d'impôt sur le revenu (lot 5).

Chaîne :
 1. population (2 % des ménages du recensement 2022) ; RFR, salaires et pensions ancrés sur l'IRCOM (revenus 2024) ;
 2. heures supplémentaires exonérées retirées des salaires imposables (masse nationale DGFiP, cases 1GH…) ;
    salaires des personnes travaillant à l'étranger (recensement) → revenus à crédit égal à l'impôt français (8TK) ;
    épargne retraite déductible (cases 6NS…) ;
 3. passe OpenFisca « salaires et pensions » → reste = RFR visé − RFR OpenFisca − heures supplémentaires ;
 4. reste réparti entre capital au prélèvement forfaitaire, revenus fonciers et d'indépendants au barème, et revenus
    inclus dans le RFR mais non imposés au barème, sous contrainte des masses nationales par case de déclaration ;
 5. dépenses ouvrant droit à crédits et réductions (emploi à domicile, garde, dons), nombres et montants nationaux ;
    réductions et crédits non modélisés un à un : calés par décile de RFR par part sur la DGFiP ;
 6. TESTS (grandeurs non utilisées pour construire) : nombre de parts et impôt au barème par décile de RFR par part ;
    impôt net par tranche de RFR (IRCOM).
Sensibilité : concentration du capital η ∈ {0,5 ; 0,8 ; 1,2}.
Sortie : outputs/validation_M4.md
"""
from __future__ import annotations

import gc
import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m4_openfisca as mo  # noqa: E402
import m4_population as m4  # noqa: E402

F = 0.02
ETAS = (0.8, 0.5, 1.2)
RECALER = True  # version 1.3 : capital au PFU calé par décile sur la DGFiP (PFU devient une donnée, plus un test)
VARS = ("nbptr", "ip_net", "prelevement_forfaitaire_unique_ir", "credits_impot", "reductions")


def cehr(fo: pd.DataFrame) -> pd.Series:
    """Contribution exceptionnelle sur les hauts revenus (art. 223 sexies du CGI), calculée sur le RFR : 3 % entre
    250 000 et 500 000 € (500 000 et 1 000 000 € pour un couple), 4 % au-delà ; sans le mécanisme de lissage.
    Calcul direct : la variable OpenFisca correspondante fait dépasser la mémoire disponible à cette taille d'échantillon."""
    k = np.where(fo.couple, 2.0, 1.0)
    r = fo.rfr.to_numpy()
    return pd.Series(0.03 * np.clip(r - 250_000 * k, 0, 250_000 * k) + 0.04 * np.clip(r - 500_000 * k, 0, None), index=fo.index)
GROUPES = [("0 à 15 000", 0, 15_000), ("15 001 à 20 000", 15_000, 20_000), ("20 001 à 30 000", 20_000, 30_000),
           ("30 001 à 50 000", 30_000, 50_000), ("50 001 à 100 000", 50_000, 100_000),
           ("100 001 à 200 000", 100_000, 200_000), ("200 001 à 1 000 000", 200_000, 1_000_000),
           ("Plus de 1 000 000", 1_000_000, np.inf)]


def groupe_tranche(ir: pd.DataFrame) -> pd.Series:
    return pd.Series({r.tranche: nom for _, r in ir.iterrows() for nom, a, b in GROUPES if a - 1 <= r.bas < b})


TMP = pathlib.Path("/tmp/validation_M4")


def _travailleur(tache: str, eta: float = 0.8):
    """Exécuté dans un processus Python neuf (voir `_lancer`) : relit les données préparées et lance OpenFisca."""
    if tache == "prep":
        ind, fo, ir, tot, cov, f8tk, reste, dep = preparer()
        stats = {"n_ind": len(ind), "pop": ind.poids.sum(), "menages": ind.groupby("men").poids.first().sum(),
                 "hs": (ind.hs * ind.poids).sum(), "sal_etr": (ind.sal_etranger * ind.poids).sum(),
                 "per": (ind.per * ind.poids).sum(), "cov": cov}
        pd.to_pickle({"fo": fo, "ir": ir, "tot": tot, "reste": reste, "stats": stats}, TMP / "resume.pkl")
        return
    d = pd.read_pickle(TMP / "prep.pkl")
    if tache == "rfr":
        r = mo.impot(d["ind"], 2024, variables=("rfr", "nbptr"), entrees_foyer={"f8tk": d["f8tk"]}, entrees_individu={"f6ns": "per"})
    else:
        r = simuler(d["ind"], d["fo"], d["tot"], d["f8tk"], d["reste"], d["dep"], eta)
    r.to_pickle(TMP / f"{tache}_{eta}.pkl")


def _lancer(tache: str, eta: float = 0.8) -> pd.DataFrame:
    """Chaque simulation OpenFisca tourne dans un processus séparé (environ 3 Go à 2 % des ménages), pour ne pas
    accumuler la mémoire de plusieurs simulations dans le même processus."""
    import subprocess
    TMP.mkdir(exist_ok=True)
    code = f"import sys; sys.path.insert(0, {str(RACINE / 'tests')!r}); import validation_M4 as v; v._travailleur({tache!r}, {eta})"
    subprocess.run([sys.executable, "-c", code], check=True)
    return None if tache == "prep" else pd.read_pickle(TMP / f"{tache}_{eta}.pkl")


def preparer():
    ind, fo, ir = m4.construire(f=F)
    tot = m4.totaux_cases(2024)
    cov = fo.poids.sum() / ir.foyers.sum()
    ind["hs"] = m4.imputer_heures_sup(ind, tot["hs_exonerees"] * cov)
    ind["salaires"] = ind.salaires - ind.hs
    hs_f = ind.hs.groupby(ind.foyer).sum().reindex(fo.index).fillna(0)
    etr = ((ind.ILT == "7") & (ind.TACT == "11")).to_numpy()
    ind["sal_etranger"] = np.where(etr, ind.salaires, 0.0)
    ind["salaires"] = ind.salaires - ind.sal_etranger
    f8tk = (0.9 * ind.sal_etranger).groupby(ind.foyer).sum().reindex(fo.index).fillna(0)
    ind["per"] = m4.imputer_epargne_retraite(ind, fo, tot["epargne_retraite"] * cov, tot["personnes_epargne_retraite"] * cov)
    pd.to_pickle({"ind": ind, "f8tk": f8tk}, TMP / "prep.pkl")
    del ind
    gc.collect()
    p0 = _lancer("rfr")
    ind = pd.read_pickle(TMP / "prep.pkl")["ind"]
    reste = (fo.rfr - p0.rfr_of - hs_f).clip(lower=0)
    fo["nbptr"] = p0.nbptr_of
    del p0
    gc.collect()
    dep = m4.imputer_depenses(fo, ind, tot, cov)
    pd.to_pickle({"ind": ind, "fo": fo, "tot": tot, "f8tk": f8tk, "reste": reste, "dep": dep}, TMP / "prep.pkl")
    return ind, fo, ir, tot, cov, f8tk, reste, dep


def simuler(ind, fo, tot, f8tk, reste, dep, eta):
    au = m4.repartir_autres(fo, reste, tot, eta_capital=eta)
    if RECALER:
        au0 = au
        cov = fo.poids.sum() / m4.charger_ircom().foyers.sum()
        au = m4.recaler_capital_deciles(fo, au, m4.deciles_rfr_par_part(fo, fo.nbptr), m4.lire_deciles_dgfip(2024),
                                        masse_bareme=(tot["foncier"] + tot["independants"]) * cov)
        au.attrs.update(au0.attrs)
    e = {"f2dc": au.dividendes, "f2tr": au.interets, "f3vg": au.plus_values, "f4ba": au.foncier + au.independants,
         "f8tk": f8tk, **{c: dep[c] for c in dep.columns}}
    r = mo.impot(ind, 2024, variables=VARS, entrees_foyer=e, entrees_individu={"f6ns": "per"})
    r["part_exoneree"] = au.attrs["part_exoneree"]  # les attrs ne traversent pas toujours le pickle
    w = fo.poids
    for nom, cols in (("masse_cap", ["dividendes", "interets", "plus_values"]), ("masse_bar", ["foncier", "independants"]),
                      ("masse_exo", ["exonere"])):
        r[nom] = float((au[cols].sum(axis=1) * w).sum())
    gc.collect()
    return r


def main():
    t0 = time.time()
    _lancer("prep")
    z = pd.read_pickle(TMP / "resume.pkl")
    fo, ir, tot, reste, st = z["fo"], z["ir"], z["tot"], z["reste"], z["stats"]
    cov = st["cov"]
    dg = m4.lire_deciles_dgfip(2024)
    w = fo.poids
    k = ir.foyers.sum() / w.sum()
    res = {}
    for eta in ETAS:
        r = _lancer("impot", eta)
        r.attrs["part_exoneree"] = float(r.pop("part_exoneree").iloc[0])
        for nom in ("masse_cap", "masse_bar", "masse_exo"):
            r.attrs[nom] = float(r.pop(nom).iloc[0])
        dec = m4.deciles_rfr_par_part(fo, r.nbptr_of)
        avant = r.ip_net_of + r.prelevement_forfaitaire_unique_ir_of + cehr(fo)
        avant = avant.where(avant >= 61, 0.0)  # seuil de mise en recouvrement (art. 1657 du CGI), avant crédits
        rici_mod = r.credits_impot_of + r.reductions_of
        resid = m4.caler_rici_residuelles(fo, avant - rici_mod, rici_mod, r.nbptr_of, dec, dg)
        r["dec"] = dec
        r["net"] = avant - rici_mod - resid
        res[eta] = r
    r = res[0.8]
    P = (r.nbptr_of * w).groupby(r.dec).sum()
    W = w.groupby(r.dec).sum()
    par_part = lambda col: (col * w).groupby(r.dec).sum() / P  # noqa: E731
    D = pd.DataFrame({"parts_m": P / W, "parts_d": dg.parts, "rfr_m": par_part(fo.rfr), "rfr_d": dg.rfr,
                      "bar_m": par_part(r.ip_net_of), "bar_d": dg.bareme,
                      "pfu_m": par_part(r.prelevement_forfaitaire_unique_ir_of), "pfu_d": dg.forfaitaire,
                      "rici_mod": par_part(r.credits_impot_of + r.reductions_of), "rici_d": dg.rici,
                      "net_m": par_part(r.net), "net_d": dg.net})
    tot_bar = {e: (res[e].ip_net_of * w).sum() * k / 1e9 for e in ETAS}
    tot_net = {e: (res[e].net * w).sum() * k / 1e9 for e in ETAS}
    bar_dgfip = (dg.bareme * dg.parts).sum() / 10 * ir.foyers.sum() / 1e9
    L = ["# Validation du lot 4 (version 1.3) — population de foyers et impôt sur le revenu 2024", "",
         f"Généré par `tests/validation_M4.py` : échantillon de {F:.0%} des ménages du recensement 2022 "
         f"({len(fo)} foyers, {st['n_ind']} personnes), durée {time.time() - t0:.0f} s. Masses ramenées aux "
         f"{ir.foyers.sum() / 1e6:.2f} M de foyers DGFiP (couverture du modèle : {cov:.1%}).", "",
         "## Couverture et masses imputées", "", "| Grandeur | Modèle | Référence |", "|---|---|---|",
         f"| Personnes des ménages ordinaires | {st['pop'] / 1e6:.2f} M | 66,3 M (Insee, RP 2022) |",
         f"| Ménages | {st['menages'] / 1e6:.2f} M | 30,9 M (Insee, RP 2022) |",
         f"| Foyers fiscaux | {w.sum() / 1e6:.2f} M | {ir.foyers.sum() / 1e6:.2f} M (DGFiP, dont 0,30 M de non-résidents) |",
         f"| Heures supplémentaires exonérées | {st['hs'] / cov / 1e9:.1f} Md€ | {tot['hs_exonerees'] / 1e9:.1f} Md€ (calé) |",
         f"| Salaires de personnes travaillant à l'étranger | {st['sal_etr'] / cov / 1e9:.1f} Md€ | {tot['salaires_etrangers_ci'] / 1e9:.1f} Md€ (cases 1AF-1CF, y c. non-résidents) |",
         f"| Épargne retraite déductible | {st['per'] / cov / 1e9:.1f} Md€ | {tot['epargne_retraite'] / 1e9:.1f} Md€ (calé) |",
         f"| Reste (RFR − salaires et pensions − heures sup.) | {(reste * w).sum() / cov / 1e9:.0f} Md€ | capital, foncier, indépendants déclarés : "
         f"{sum(tot[c] for c in ('dividendes', 'interets', 'plus_values', 'foncier', 'independants')) / 1e9:.0f} Md€ ; "
         f"excédent traité comme inclus dans le RFR mais non imposé au barème : {r.attrs['part_exoneree']:.0%} du reste |", "",
         f"| Répartition du reste après calage du capital par décile (η = 0,8) | capital {r.attrs['masse_cap'] / cov / 1e9:.0f} ; barème {r.attrs['masse_bar'] / cov / 1e9:.0f} ; exonéré {r.attrs['masse_exo'] / cov / 1e9:.0f} Md€ | "
         f"déclaré : capital {(tot['dividendes'] + tot['interets'] + tot['plus_values']) / 1e9:.0f} ; foncier et indépendants {(tot['foncier'] + tot['independants']) / 1e9:.0f} Md€ |", "",
         "## Test 1 : par décile de RFR par part (DGFiP, revenus 2024), η = 0,8", "",
         "Grandeurs testées : nombre de parts, impôt au barème par part. Le PFU par part est calé (version 1.3). Les réductions et crédits (RICI) non modélisés "
         "un à un sont calés par décile ; la colonne « RICI modélisés » montre la part reconstituée sans calage. Euros par part ; "
         "valeurs DGFiP arrondies à 10 €.", "",
         "| Décile | Parts, modèle | Parts, DGFiP | RFR/part, modèle | RFR/part, DGFiP | Barème/part, modèle | Barème/part, DGFiP | PFU/part, modèle | PFU/part, DGFiP | RICI modélisés/part | RICI/part, DGFiP | IR net/part, modèle | IR net/part, DGFiP |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for d, x in D.iterrows():
        L.append(f"| {d} | {x.parts_m:.2f} | {x.parts_d:.2f} | {x.rfr_m:,.0f} | {x.rfr_d:,.0f} | {x.bar_m:,.0f} | {x.bar_d:,.0f} | "
                 f"{x.pfu_m:,.0f} | {x.pfu_d:,.0f} | {x.rici_mod:,.0f} | {x.rici_d:,.0f} | {x.net_m:,.0f} | {x.net_d:,.0f} |".replace(",", " "))
    L += ["", f"Impôt au barème total : modèle {tot_bar[0.8]:.1f} Md€ (η = 0,5 : {tot_bar[0.5]:.1f} ; η = 1,2 : {tot_bar[1.2]:.1f}) ; "
          f"DGFiP ≈ {bar_dgfip:.1f} Md€ (déduit des moyennes par décile).", "",
          "## Test 2 : impôt net par tranche de RFR (IRCOM), η = 0,8", "",
          "| Tranche de RFR | Part imposée, modèle | Part imposée, DGFiP | Impôt net, modèle (Md€) | Impôt net, DGFiP (Md€) |", "|---|---|---|---|---|"]
    gr = groupe_tranche(ir)
    fo["groupe"] = fo.tranche.map(gr)
    for g, _, _ in GROUPES:
        m = fo.groupe == g
        sub = ir[ir.tranche.map(gr) == g]
        kg = sub.foyers.sum() / w[m].sum()
        imp_d = sub.foyers_imposes.sum() / sub.loc[sub.foyers_imposes.notna(), "foyers"].sum()
        L.append(f"| {g} | {(w[m] * (r.net[m] > 0)).sum() / w[m].sum():.0%} | {imp_d:.0%} | {(r.net[m] * w[m]).sum() * kg / 1e9:.1f} | {sub.impot.sum() / 1e9:.1f} |")
    L.append(f"| **Total** | | | **{(r.net * w).sum() * k / 1e9:.1f}** | **{ir.impot.sum() / 1e9:.1f}** |")
    L += ["", f"Sensibilité de l'impôt net total à η : {tot_net[0.5]:.1f} (η = 0,5), {tot_net[0.8]:.1f} (0,8), {tot_net[1.2]:.1f} (1,2) Md€.", ""]
    (RACINE / "outputs" / "validation_M4.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
