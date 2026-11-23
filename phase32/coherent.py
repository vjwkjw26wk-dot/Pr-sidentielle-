import sys
sys.argv=['x']
from exp import *
import backtest as BT
def weights(mod): return {b:float(mod.hist[b].n[mod.B]) for b in mod.BR}
def g_coherent(mod, ex):
    """Tendance de productivité par tête cohérente avec la fonction de production, information ≤ origine :
    g_N = g_PGF/(1−α) + α/(1−α)·(g_K − g_Y) au rythme prévu par le potentiel de référence (K et Y à leur tendance).
    On translate toutes les branches du même écart (préserve l'hétérogénéité de branche)."""
    lp=ex.lpgf; B=mod.B; a=M.ALPHA_K
    gtfp=float(lp[B]-lp[B-8])/8
    lk=ex.lk_ref; ly=ex.lpot_ref
    gk=float(lk[B+2]-lk[B+1]); gy=float(ly[B+2]-ly[B+1])
    cible=gtfp/(1-a)+a/(1-a)*(gk-gy)
    w=weights(mod); W=sum(w.values()); moy=sum(mod.g_prod[b]*w[b] for b in mod.BR)/W
    for b in mod.BR: mod.g_prod[b]+=cible-moy
    return cible,moy
INFO={}
def make(mode,rho,a,th,coh,B=2010,fin=2019):
    mod,ex,ans=BT.construire(B,fin,rho,a,th,mode)
    if coh: INFO[(mode,coh,B)]=g_coherent(mod,ex)
    M.EXP.clear(); r=mod.simuler(ans,ex); o=BT.observe(mod)
    em=mod.emp; t=fin
    e=lambda k: float(np.sqrt(np.mean([(r[k][y]-o[k][y])**2 for y in ans])))
    return dict(dette=float(r.dette_pib[t]-o['dette_pib'][t]),pib=float(100*(r.pib[t]/o['pib'][t]-1)),emploi=float(100*(r.emploi[t]/em.emploi[t]-1)),
                chomage=float(r.chomage[t]-o['chomage'][t]),pc=float(100*(r.pc[t]/o['pc'][t]-1)),
                rmse_pib=float(np.sqrt(np.mean([(100*(r.pib[y]/r.pib[y-1]-1) - 100*(o['pib'][y]/o['pib'][y-1]-1))**2 for y in ans if y-1 in r.index or y-1==B] ))) if False else np.nan,
                rmse_chomage=e('chomage'),rmse_dette=e('dette_pib'),ecart_prod_2019=float(r.ecart_production[t]),Z_fin=float(r.supplement_demande_fermeture[t]/r.pib[t]*100) if 'supplement_demande_fermeture' in r else np.nan)
rows={}
for B in (2010,2012,2014):
    for nom,(mode,rho,a,th) in {'v08':('production',0.2,0.0,0.75),'v06':('chomage',0.15,0.3,0.0),'demande':('production',0.0,0.0,0.0)}.items():
        for coh in (False,True):
            rows[f'{B} {nom}{" + productivité cohérente" if coh else ""}']=make(mode,rho,a,th,coh,B)
print(pd.DataFrame(rows).T.drop(columns=['rmse_pib']).round(2).to_string())
print({k:(round(100*v[0],2),round(100*v[1],2)) for k,v in INFO.items()})
