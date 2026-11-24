"""Phase 5, lot 5.3 (préparation) : tableau de robustesse automatique d'un programme test sur 10 régimes."""
import pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R), str(R / "phase5")]
import pandas as pd
import m23_regimes as G
env = G.Environnement.charger("p4", "part_constante")

def baisse_impots(mod, ex):
    niv = dict(ex.niveaux or {}); s = niv.get("impots_menages_pib", pd.Series(dtype=float)).copy()
    for t in range(2027, 2048):
        s[t] = float(s.get(t, 0.0)) - 0.5
    niv["impots_menages_pib"] = s.sort_index(); ex.niveaux = niv
t0 = time.time()
df = G.robustesse(env, G.Programme("baisse d'impôts des ménages −0,5 pt de PIB", baisse_impots))
pd.set_option("display.width", 250)
print(df.round(2).to_string()); print(f"{time.time() - t0:.0f} s")
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "lot53_robustesse_test.csv")
