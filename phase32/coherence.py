import sys
sys.argv=['x']
from exp import *
import backtest as BT
out={}
for nom,(rho,a,th,mode) in {'v08':(0.2,0.0,0.75,'production'),'v06':(0.15,0.3,0.0,'chomage')}.items():
    mod,ex,ans=BT.construire(2010,2019,rho,a,th,mode)
    M.EXP.clear(); r=mod.simuler(ans,ex)
    us=ex.chomage_structurel
    lp=ex.lpgf; gtfp=float(lp[2019]-lp[2010])/9
    o=BT.observe(mod)
    T=pd.DataFrame({'écart production sim (%)':r.ecart_production,'u sim':r.chomage,'u* temps réel':pd.Series({t:float(us[t]) for t in ans}),
                    '−Okun×(u−u*)':-1.5*(r.chomage-pd.Series({t:float(us[t]) for t in ans})),'u obs':o['chomage'].loc[2011:2019],
                    'Z fermeture (% PIB)':100*r.supplement_demande_fermeture/ (r.pib) if 'supplement_demande_fermeture' in r else np.nan}).loc[list(ans)]
    print('==',nom,' croissance PGF en temps réel %.2f %%/an → productivité du travail potentielle à K/Y constant %.2f %%/an'%(100*gtfp,100*gtfp/(1-M.ALPHA_K)))
    print(T.round(2).to_string())
