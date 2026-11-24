"""Phase 5, lot 5.3 : sensibilité des effets de S1-S5 aux paramètres structurels modifiables sans recalibration."""
import pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import pandas as pd
import m23_regimes as G, m25_programmes as P
OUT = pathlib.Path(__file__).parent / "resultats"
TR = pickle.load(open(OUT / "lot53_traductions.pkl", "rb"))
env = G.Environnement.charger("p4", "part_constante")
NOMS = ["PSI_TAUX", "PSI_CHOMAGE", "SEMI_ELAST_IS", "THETA_TRESORERIE", "mu_taux", "div_lissage", "bund_transmission", "prime_dette"]
t0 = time.time(); out = {}
for k, tr in TR.items():
    out[k] = G.sensibilite_structurelle(env, P.programme(tr), NOMS, horizons=(10, 20))
    print("fait", k, round(time.time() - t0), flush=True)
df = pd.concat(out, names=["stratégie"]); df.to_csv(OUT / "lot53_structurels_S1_S5.csv")
