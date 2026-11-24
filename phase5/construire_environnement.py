"""Phase 5 (lot 5.0) : calibration de l'environnement (une seule fois par configuration × convention de dépense),
mise en cache dans outputs/. Usage : python3 phase5/construire_environnement.py p4 part_constante|historique"""
import pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import m23_regimes as G

if __name__ == "__main__":
    conf, conv = sys.argv[1], sys.argv[2]
    t0 = time.time()
    env = G.Environnement.charger(conf, conv)
    print(f"environnement {conf} / {conv} : {time.time() - t0:.0f} s", flush=True)
    tr = env.reference
    print(tr[["pib", "chomage", "solde_pib", "dette_pib"]].loc[[2025, 2027, 2031, 2035, 2040, 2047]].round(2).to_string())
