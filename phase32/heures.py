import sys
sys.argv=['x']
from exp import *
import backtest as BT
def dlog(s,a,b): return float(np.log(s[b]/s[a])/(b-a))
def run_h(B, spec, mode='production', rho=0.2, a=0.0, th=0.75, fin=2019):
    mod,ex,ans=BT.construire(B,fin,rho,a,th,mode)
    if spec!='v08':
        for b in mod.BR:
            h=mod.hist[b]; hpt=h.h/h.n
            g_heure=float(np.mean([np.log(h.q[t]/h.q[t-1])-np.log(h.h[t]/h.h[t-1]) for t in range(B-7,B+1)]))   # même fenêtre que g_prod
            if spec=='heures/tête nulles (temps réel)': mod.g_prod[b]=g_heure
            elif spec=='heures/tête observées [oracle]': mod.g_prod[b]=g_heure+dlog(hpt,B,fin)
    M.EXP.clear(); r=mod.simuler(ans,ex); o=BT.observe(mod); em=mod.emp; t=fin
    mk_obs=sum(mod.hist[b].n for b in mod.BR)
    e=lambda k: float(np.sqrt(np.mean([(r[k][y]-o[k][y])**2 for y in ans])))
    return dict(dette=float(r.dette_pib[t]-o['dette_pib'][t]),pib=float(100*(r.pib[t]/o['pib'][t]-1)),emploi=float(100*(r.emploi[t]/em.emploi[t]-1)),
                chomage=float(r.chomage[t]-o['chomage'][t]),pc=float(100*(r.pc[t]/o['pc'][t]-1)),rmse_chomage=e('chomage'),rmse_dette=e('dette_pib'),
                Z_fin=float(r.supplement_demande_fermeture[t]/r.pib[t]*100))
# poids : tendance agrégée
mod,ex,ans=BT.construire(2010,2019,0.2,0,0.75,'production')
w={b:float(mod.hist[b].n[2010]) for b in mod.BR}; W=sum(w.values())
gh=sum(w[b]*float(np.mean([np.log(mod.hist[b].q[t]/mod.hist[b].q[t-1])-np.log(mod.hist[b].h[t]/mod.hist[b].h[t-1]) for t in range(2003,2011)])) for b in mod.BR)/W
gn=sum(w[b]*mod.g_prod[b] for b in mod.BR)/W
print('tendances pondérées 2003-2010 : par tête %.2f %%/an, par heure %.2f %%/an'%(100*gn,100*gh))
rows={}
for B in (2010,2012):
    for clos,(mode,rho,a,th) in {'v08':('production',0.2,0.0,0.75),'v06':('chomage',0.15,0.3,0.0)}.items():
        for spec in ('v08','heures/tête nulles (temps réel)','heures/tête observées [oracle]'):
            rows[f'{B} {clos} | {spec if spec!="v08" else "référence"}']=run_h(B,spec,mode,rho,a,th)
print(pd.DataFrame(rows).T.round(2).to_string())
