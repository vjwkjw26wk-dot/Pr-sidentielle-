from exp_depenses import *
import m7_equations as E
def mk_err(r,mod,t=2019):
    em=mod.emp; nm_obs=em.emploi-sum(mod.hist[b].n for b in mod.BR)
    nm_sim=mod.n_nm0*1.0
    return None
CAPN={}
def run2(exp=None, **kw):
    res,r,mod=run(exp=exp, **kw)
    # emploi marchand simulé vs observé
    mk_obs=sum(mod.hist[b].n for b in mod.BR)
    # emploi marchand simulé = emploi total - n_nm simulé : on le récupère via la sortie emploi_industrie ? on recalcule
    res['emploi_marchand']=float(100*((r.emploi[2019]-CAPN.get('nm',{}).get(2019,np.nan))/mk_obs[2019]-1)) if CAPN.get('nm') else np.nan
    q_obs=sum(mod.hist[b].q for b in mod.BR)
    return res,r,mod
# capture n_nm simulé
def nm_capture(f):
    def g(self,t,q,n):
        v=f(self,t,q,n) if f else n
        CAPN.setdefault('nm',{})[t]=v; return v
    return g
def gprod_oracle(mod):
    apres(mod)
    for b in mod.BR:
        h=mod.hist[b]; mod.g_prod[b]=float(np.mean([np.log(h.q[t]/h.q[t-1])-np.log(h.n[t]/h.n[t-1]) for t in range(2011,2020)]))
def gprod_print(mod):
    apres(mod)
    w={b:float(mod.hist[b].n[2010]) for b in mod.BR}; W=sum(w.values())
    print('g_prod moyen pondéré (2003-2010, utilisé) : %.2f %%/an'%(100*sum(mod.g_prod[b]*w[b] for b in mod.BR)/W))
    print('c_emp moyen pondéré : %.3f %%/an'%(100*sum(mod.c_emp[b]*w[b] for b in mod.BR)/W))
def cemp0(mod):
    apres(mod)
    for b in mod.BR: mod.c_emp[b]=0.0
def both(mod):
    gprod_oracle(mod)
    for b in mod.BR: mod.c_emp[b]=0.0
def sig0(): E.SIGMA_TRAVAIL=0.0
def nolk(mod,ex): ex.lk_ref=None
rows={}
for base_nom,base in [('v08',{}),('E1b+E2',{'n_nm':nm_trend,'wpub':wpub})]:
    CAPN.clear(); b=dict(base); b['n_nm']=nm_capture(base.get('n_nm'))
    rows[base_nom]=run2(exp=b,apres_init=gprod_print)[0]
    CAPN.clear(); rows[base_nom+' | M1 g_prod observé 2011-19 [oracle]']=run2(exp=b,apres_init=gprod_oracle)[0]
    CAPN.clear(); rows[base_nom+' | M2 σ = 0 (pas d\'effet coût)']=run2(exp=b,apres_init=apres,avant_init=sig0)[0]
    CAPN.clear(); rows[base_nom+' | M3 constantes c_emp = 0']=run2(exp=b,apres_init=cemp0)[0]
    CAPN.clear(); rows[base_nom+' | M4 sans terme capital (cible_k)']=run2(exp=b,apres_init=apres,ex_mod=nolk)[0]
    CAPN.clear(); rows[base_nom+' | M1+M3']=run2(exp=b,apres_init=both)[0]
df=pd.DataFrame(rows).T[['dette','emploi','emploi_marchand','chomage','pib','pc','pibn','rmse_dette','rmse_chomage']]
print(df.round(2).to_string())
