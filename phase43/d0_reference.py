"""Phase 4.4 : trajectoire de référence à politique inchangée 2023-2047 (base 2022, recalée sur 2023-2025, FMI 2026-2031)
pour une configuration donnée ; sert de base aux chocs d'intégration (d1_chocs_integration.py).
Usage : python3 phase43/d0_reference.py v09|p4|t1"""
import pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import m8_modele as M8
import m8_reference as RF
CONF = {"v09": lambda: M8.configurer_v09(), "p4": lambda: M8.configurer_phase4(), "t1": lambda: M8.configurer_v09(prix_va="frontiere", tension_prix="aucune"),
        "v08": lambda: M8.configurer_v08()}


def reference(nom, fin=2047):
    M8.configurer_v08(); CONF[nom]()
    mod = M8.Modele(2022)
    d = RF.compte_reference(mod, range(2023, fin + 1), journal=lambda *a: None)
    return mod, d


if __name__ == "__main__":
    nom = sys.argv[1]
    t0 = time.time()
    mod, d = reference(nom)
    tr = d["trajectoire"]
    print(nom, "ok", round(time.time() - t0), "s", flush=True)
    cols = [c for c in ["pib", "chomage", "pc", "ecart_production", "solde_pib", "dette_pib", "taux_epargne", "taux_marge", "dividendes_distribues", "dette_s11", "taux_autofinancement"] if c in tr]
    print(tr[cols].loc[[2025, 2026, 2028, 2031, 2035, 2040, 2047]].round(3).to_string(), flush=True)
