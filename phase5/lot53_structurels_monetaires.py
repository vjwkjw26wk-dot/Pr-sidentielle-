"""Phase 5, lot 5.3 (correction) : sensibilité des effets de S1-S5 aux paramètres monétaires, évalués sous le régime
R2 + BCE + prime souveraine (la première passe les évaluait à taux exogènes, effet nul par construction)."""
import pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import pandas as pd
import m23_regimes as G, m25_programmes as P
OUT = pathlib.Path(__file__).parent / "resultats"
TR = pickle.load(open(OUT / "lot53_traductions.pkl", "rb"))
env = G.Environnement.charger("p4", "part_constante")
NOMS = ["bund_transmission", "menages_vitesse", "entreprises_vitesse", "bce_inflation", "bce_activite", "prime_dette", "prime_solde"]
t0 = time.time(); out = {}
for k, tr in TR.items():
    df = G.sensibilite_structurelle(env, P.programme(tr), NOMS, horizons=(10, 20))
    out[k] = df.drop(index="central", level=0)
    print("fait", k, round(time.time() - t0), flush=True)
pd.concat(out, names=["stratégie"]).to_csv(OUT / "lot53_structurels_monetaires_S1_S5.csv")
