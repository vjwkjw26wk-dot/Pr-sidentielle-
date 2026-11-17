"""Audit des mécanismes de transmission (novembre 2026) : cinq variantes de référence et décomposition par canal.

Variantes (entrée en vigueur en 2028, calendrier du simulateur, trajectoire de référence « politique inchangée ») :
  1. salaires +2 % (choc ponctuel sur le salaire par tête en 2028) ;
  2. taux normal d'IS de 25,8 % à 20 % ;
  3. consommation publique +1 point de PIB ;
  4. réindustrialisation : parts importées −20 % dans six filières (chimie, pharmacie, métallurgie, électronique,
     équipements électriques, automobile), deux versions : immédiate sans coût (borne haute) et progressive en 5 ans
     avec investissement de capacité et surcoût de 10 % ;
  5. prix de l'énergie importée +50 % (houille et pétrole brut, produits raffinés, électricité-gaz).

Décomposition par neutralisation de canaux (chaque canal est neutralisé dans la référence ET dans la variante) :
  - « effet direct » : consommation, salaires et fermeture d'offre neutralisés (production induite par le tableau
    entrées-sorties et les importations seulement) ;
  - « + revenus et consommation (induit) » : consommation réactivée ;
  - « + prix et salaires » : boucle prix-salaires réactivée ;
  - « complet » : fermeture d'offre réactivée (modèle du simulateur).
  Contrôle supplémentaire : modèle complet avec facteur commun d'importation figé (sans réponse des importations).
Sortie : outputs/audit_variantes.md et .json.  Usage : python3 tests/audit_variantes.py [avant|apres]
"""
from __future__ import annotations

import contextlib
import copy
import json
import pathlib
import sys
import time
from types import SimpleNamespace

import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE))
import m7_equations as E  # noqa: E402
import m8_modele as M  # noqa: E402
import m8_reference as RF  # noqa: E402

DEBUT, ANS = 2028, range(2023, 2036)
ENERGIE = ("CPA_B", "CPA_C19", "CPA_D")
FILIERES = ["CPA_C20", "CPA_C21", "CPA_C24", "CPA_C26", "CPA_C27", "CPA_C29"]
VARS = ["pib", "c", "fbcf", "x", "m", "emploi", "chomage", "pc", "salaire", "rdb", "solde_pib", "dette_pib"]
VARS_OPT = ["rnb", "solde_exterieur", "pib_nominal"]


@contextlib.contextmanager
def neutraliser(mod, canaux):
    """Neutralise des canaux en remplaçant temporairement des paramètres estimés."""
    sauv = {k: mod.eq[k].res for k in ("consommation", "salaires")}
    phil = E.PHILLIPS
    try:
        if "conso" in canaux:
            p = sauv["consommation"].params.copy()
            p[:] = 0.0
            mod.eq["consommation"].res = SimpleNamespace(params=p)
        if "salaires" in canaux:
            p = sauv["salaires"].params.copy()
            p[:] = 0.0
            mod.eq["salaires"].res = SimpleNamespace(params=p)
            E.PHILLIPS = 0.0
        yield
    finally:
        for k, v in sauv.items():
            mod.eq[k].res = v
        E.PHILLIPS = phil


def variantes(mod, ref):
    pibb = mod.macro.pib_cp[mod.B]
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    out = {}
    v = copy.deepcopy(ref); v.choc_salaire = pd.Series({DEBUT: 0.02}); out["1. Salaires +2 % (choc ponctuel 2028)"] = v
    v = copy.deepcopy(ref); v.taux_is = pd.Series({t: (x if t < DEBUT else 20.0) for t, x in v.taux_is.items()})
    if hasattr(M.Modele, "_profits"):        # version 0.5 : distribution des profits (M14), comme dans le simulateur
        tau0 = float(ref.taux_is.get(DEBUT, ref.taux_is.iloc[-1]))
        v.mesure_menages = {"profits": 0.15 * float(mod.apu.d5rec[mod.B]) * (tau0 - 20.0) / tau0, "annee": mod.B, "debut": DEBUT,
                            "impots": 0.0, "prestations": 0.0}
    out["2. IS de 25,8 % à 20 %"] = v
    v = copy.deepcopy(ref)
    v.conso_publique = v.conso_publique * pd.Series({t: (1 + 0.01 * pibb / g_part if t >= DEBUT else 1.0) for t in v.conso_publique.index})
    out["3. Consommation publique +1 pt de PIB"] = v
    v = copy.deepcopy(ref); v.parts_importees = {p: 0.8 for p in FILIERES}; v.phi_impose = "central"
    out["4a. Réindustrialisation −20 %, immédiate, sans coût (borne haute)"] = v
    v = copy.deepcopy(ref); v.reindustrialisation = {"produits": {p: 0.8 for p in FILIERES}, "debut": DEBUT, "duree": 5, "surcout": 0.10}
    v.phi_impose = "central"; out["4b. Réindustrialisation −20 % en 5 ans, investissement et surcoût 10 %"] = v
    v = copy.deepcopy(ref)
    for p in ENERGIE:
        v.prix_import[p] = [x * (1.5 if t >= DEBUT else 1.0) for t, x in zip(v.prix_import.index, v.prix_import[p])]
    out["5. Prix de l'énergie importée +50 %"] = v
    return out


def ecarts(r, c):
    e = {}
    for k in VARS:
        if k in ("chomage", "solde_pib", "dette_pib"):
            e[k] = {t: float(r[k][t] - c[k][t]) for t in r.index if DEBUT <= t <= 2032}
        elif k == "emploi":
            e[k] = {t: float(r[k][t] - c[k][t]) for t in r.index if DEBUT <= t <= 2032}
        else:
            e[k] = {t: float((r[k][t] / c[k][t] - 1) * 100) for t in r.index if DEBUT <= t <= 2032}
    for k in VARS_OPT:
        if k in r.columns:
            e[k] = {t: float(r[k][t] - c[k][t]) for t in r.index if DEBUT <= t <= 2032}
    # épargne des ménages : taux d'épargne approché (RDB − consommation nominale) / RDB, écart en points
    s = lambda d, t: 100 * (1 - d.c[t] * d.pc[t] / d.rdb[t])  # noqa: E731
    e["taux_epargne"] = {t: float(s(r, t) - s(c, t)) for t in r.index if DEBUT <= t <= 2032}
    e["m_sur_dd"] = None
    return e


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "avant"
    t0 = time.time()
    mod = M.Modele(2022)
    ref = RF.exogenes_variante(mod, ANS, "inchangee", journal=lambda *a: None)
    configs = {"direct": {"conso", "salaires", "fermeture"}, "induit": {"salaires", "fermeture"}, "prix": {"fermeture"}, "complet": set()}
    VS = variantes(mod, ref)
    res = {}
    for cfg, canaux in configs.items():
        with neutraliser(mod, canaux):
            rr = copy.deepcopy(ref)
            if "fermeture" in canaux:
                rr.fermeture_offre = 0.0
            c = mod.simuler(ANS, rr)
            for nom, v0 in VS.items():
                v = copy.deepcopy(v0)
                if "fermeture" in canaux:
                    v.fermeture_offre = 0.0
                if isinstance(v.phi_impose, str):
                    v.phi_impose = c.phi
                r = mod.simuler(ANS, v)
                res.setdefault(nom, {})[cfg] = ecarts(r, c)
                if cfg == "complet":
                    v2 = copy.deepcopy(v0); v2.phi_impose = c.phi
                    res[nom]["imports_figes"] = ecarts(mod.simuler(ANS, v2), c)
                    # part du supplément de demande finale servie par les importations : ΔM / Δ(PIB + M), volumes 2030
                    dm = r.m[2030] - c.m[2030]
                    dd = (r.pib[2030] - c.pib[2030]) + dm
                    res[nom]["complet"]["m_sur_dd"] = float(dm / dd) if abs(dd) > 1e-6 else None
        print(cfg, f"{time.time() - t0:.0f} s", flush=True)
    (RACINE / "outputs" / f"audit_variantes_{tag}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    L = [f"# Audit des variantes ({tag})", "", "Écarts à la référence « politique inchangée », mesures en 2028. PIB, consommation, "
         "investissement, exportations, importations, prix, salaire, revenu disponible en % ; emploi en milliers ; chômage, solde, dette "
         "et taux d'épargne en points.", ""]
    for nom, d in res.items():
        L += [f"## {nom}", "", "| Configuration | Année | PIB | Conso. | FBCF | Export. | Import. | Emploi | Chômage | Prix conso. | Salaire | RDB | Taux d'épargne | Solde | Dette |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for cfg in ("direct", "induit", "prix", "complet", "imports_figes"):
            for t in (2028, 2030, 2032):
                e = d[cfg]
                L.append(f"| {cfg} | {t} | " + " | ".join(
                    f"{e[k][t]:+.0f}" if k == "emploi" else f"{e[k][t]:+.2f}"
                    for k in ("pib", "c", "fbcf", "x", "m", "emploi", "chomage", "pc", "salaire", "rdb", "taux_epargne", "solde_pib", "dette_pib")) + " |")
        if "rnb" in d["complet"]:
            e = d["complet"]
            L += ["", "Revenu national (modèle complet) : écart de RNB nominal " + ", ".join(f"{t} : {e['rnb'][t] / 1e3:+.1f} Md€" for t in (2028, 2030, 2032))
                  + " ; écart de PIB nominal " + ", ".join(f"{t} : {e['pib_nominal'][t] / 1e3:+.1f} Md€" for t in (2028, 2030, 2032))
                  + " ; solde extérieur " + ", ".join(f"{t} : {e['solde_exterieur'][t] / 1e3:+.1f} Md€" for t in (2028, 2030, 2032)) + "."]
        if d["complet"].get("m_sur_dd") is not None:
            L += ["", f"Part de la demande finale supplémentaire servie par les importations, ΔM / Δ(PIB + M), volumes 2030 : {d['complet']['m_sur_dd']:.2f}"]
        L.append("")
    (RACINE / "outputs" / f"audit_variantes_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"fini en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
