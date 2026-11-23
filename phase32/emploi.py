import sys, pathlib
import numpy as np, pandas as pd
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'src'),str(R),str(R/'phase31')]
import backtest as BT, m8_modele as M
B=int(sys.argv[1]) if len(sys.argv)>1 else 2010
mod,ex,ans=BT.construire(B,2019,0.2,0.0,0.75,'production')
r=mod.simuler(ans,ex)
S=pd.read_csv(f'dep_sim_{B}.csv',index_col=0)
em=mod.emp; m=mod.macro
nm_obs=em.emploi - sum(mod.hist[b].n for b in mod.BR)
mk_obs=em.emploi-nm_obs
nm_sim=mod.n_nm0*S.nnm_idx; mk_sim=r.emploi.loc[list(ans)]-nm_sim
print('n_nm0 (milliers)', round(mod.n_nm0), ' emploi total B', round(em.emploi[B]))
T=pd.DataFrame({'total_err%':(r.emploi/em.emploi-1)*100,'marchand_err%':(mk_sim/mk_obs-1)*100,'nonmarch_err%':(nm_sim/nm_obs-1)*100,
  'contrib_nm_pts':(nm_sim-nm_obs)/em.emploi*100,'contrib_mk_pts':(mk_sim-mk_obs)/em.emploi*100}).loc[list(ans)]
print(T.round(2).to_string())
# VA et productivité marchande
va_mk_obs=sum(mod.hist[b].q for b in mod.BR)
print('\nVA non marchande volume obs (indice):', (m.pib.loc[B:2019]*0).to_dict() if False else '')
# productivité non marchande observée avant l'origine
qnm=None
for b in mod.hist:
    pass
print('branches', mod.BR, list(mod.hist.keys())[:20])
