import sys, pathlib, json
import numpy as np, pandas as pd
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'src'),str(R),str(R/'phase31')]
import backtest as BT, m8_modele as M
CAP={}
orig=M.Modele._finances
def wrap(self,t,A,niv,mb,ab,ex,w,n_br,n_nm,pc,pib_vol,q_br,pva):
    out=orig(self,t,A,niv,mb,ab,ex,w,n_br,n_nm,pc,pib_vol,q_br,pva)
    B=self.B
    g_vol=float(ex.conso_publique[t])/float(ex.conso_publique[B])
    CAP[t]=dict(d1p=ab.d1pay*(w/A['w'][B])*(n_nm/self.n_nm0), p3a=(ab.p3-ab.d1pay)*g_vol*pc/A['pc'][B],
                d62=out['prestations'], d41=out['interets'], te=out['depenses'], pibn=out['pib_nominal'],
                w_idx=w/A['w'][B], nnm_idx=n_nm/self.n_nm0, pc_idx=pc/A['pc'][B], g_idx=g_vol, tapp=out['taux_apparent'])
    return out
M.Modele._finances=wrap
B=int(sys.argv[1]) if len(sys.argv)>1 else 2010
mod,ex,ans=BT.construire(B,2019,0.2,0.0,0.75,'production')
r=mod.simuler(ans,ex)
S=pd.DataFrame(CAP).T.loc[list(ans)]
S['autres']=S.te-S.d1p-S.p3a-S.d62-S.d41
a=mod.apu; m=mod.macro; em=mod.emp
nm_obs=em.emploi - sum(mod.hist[b].n for b in mod.BR)
O=pd.DataFrame({'d1p':a.d1pay,'p3a':a.p3-a.d1pay,'d62':a.d62pay,'d41':a.d41pay,'te':a.te,'pibn':m.pib_cp,
   'w_idx':(mod.men.d1/em.emploi)/(mod.men.d1/em.emploi)[B] if False else np.nan})
O['autres']=O.te-O.d1p-O.p3a-O.d62-O.d41
O=O.loc[list(ans)]
# indices observés
wpriv=pd.Series({t:sum(mod.hist[b].wb[t] for b in mod.BR)/sum(mod.hist[b].ns[t] for b in mod.BR) for t in range(B,2020)})
wpub=(a.d1pay/nm_obs)
idx=pd.DataFrame({'w_marchand_obs':wpriv/wpriv[B],'w_public_obs':(wpub/wpub[B]).loc[B:2019],'nnm_obs':(nm_obs/nm_obs[B]).loc[B:2019],
   'pc_obs':(m.p_c/m.p_c[B]).loc[B:2019],'p3_defl_obs':((a.p3/m.g)/(a.p3/m.g)[B]).loc[B:2019],'g_obs':(m.g/m.g[B]).loc[B:2019]}).loc[list(ans)]
print('reproduction dette_pib 2019 :', round(float(r.dette_pib[2019]),2))
pct=lambda D: D[['d1p','p3a','d62','d41','autres','te']].div(D.pibn,axis=0)*100
ps,po=pct(S),pct(O)
print('\n% PIB simulé / observé / écart')
for c in ['d1p','p3a','d62','d41','autres','te']:
    print(c.ljust(7),' '.join(f'{ps[c][t]:5.2f}/{po[c][t]:5.2f}({ps[c][t]-po[c][t]:+.2f})' for t in ans))
E=(ps-po); print('\ncumul écart (pts PIB·an) :', E.sum().round(2).to_dict())
# en niveau M€ (pour séparer numérateur et dénominateur)
print('\nécart en % du niveau (M€) 2019 :', ((S.loc[2019,['d1p','p3a','d62','d41','autres','te','pibn']]/O.loc[2019,['d1p','p3a','d62','d41','autres','te','pibn']]-1)*100).round(2).to_dict())
print('\nindices simulés 2019 :', S.loc[2019,['w_idx','nnm_idx','pc_idx','g_idx']].round(3).to_dict())
print('indices observés :\n', idx.round(3).to_string())
S.to_csv(f'dep_sim_{B}.csv'); O.to_csv(f'dep_obs_{B}.csv'); idx.to_csv(f'idx_obs_{B}.csv')
