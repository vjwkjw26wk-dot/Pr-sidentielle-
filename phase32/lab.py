"""Banc d'essai phase 3.2 : variantes isolées du backtest (copie exp_src ; v0.8 inchangée)."""
import sys, pathlib
import numpy as np, pandas as pd
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(pathlib.Path(__file__).resolve().parent/'exp_src'),str(R/'src'),str(R),str(R/'phase31')]
import m8_modele as M
import backtest as BT
assert 'exp_src' in M.__file__
CLOS={'v08':('production',0.2,0.0,0.75),'v06':('chomage',0.15,0.3,0.0),'demande':('production',0.0,0.0,0.0)}
def chom_obs(self,t):
    u=float(self.macro.chomage[t])/100; n=float(self.emp.emploi[t]); return u*n/(1-u)
def tendance_heure(mod):
    B=mod.B
    for b in mod.BR:
        h=mod.hist[b]
        mod.g_prod[b]=float(np.mean([np.log(h.q[t]/h.q[t-1])-np.log(h.h[t]/h.h[t-1]) for t in range(B-7,B+1)]))
def run(B=2010, fin=2019, clos='v08', exp=None, heures=False, ex_mod=None, mod_mod=None, construire_kw=None, retour=False):
    mode,rho,a,th=CLOS[clos]
    mod,ex,ans=BT.construire(B,fin,rho,a,th,mode,**(construire_kw or {}))
    if heures: tendance_heure(mod)
    if mod_mod: mod_mod(mod)
    if ex_mod: ex_mod(mod,ex)
    M.EXP.clear(); M.EXP.update(exp or {})
    r=mod.simuler(ans,ex); M.EXP.clear()
    o=BT.observe(mod); em=mod.emp; t=fin
    rm=lambda k: float(np.sqrt(np.mean([(r[k][y]-o[k][y])**2 for y in ans if y in o[k].index])))
    gr=lambda s,y,ref: 100*(s[y]/(s[y-1] if y-1 in s.index else ref[y-1])-1)
    rmg=lambda k,rk: float(np.sqrt(np.mean([(gr(r[rk],y,o[k])-gr(o[k],y,o[k]))**2 for y in ans])))
    res=dict(dette=float(r.dette_pib[t]-o['dette_pib'][t]), solde=float(r.solde_pib[t]-o['solde_pib'][t]),
             pib=float(100*(r.pib[t]/o['pib'][t]-1)), emploi=float(100*(r.emploi[t]/em.emploi[t]-1)),
             chomage=float(r.chomage[t]-o['chomage'][t]), pc=float(100*(r.pc[t]/o['pc'][t]-1)),
             pibn=float(100*(r.pib_nominal[t]/mod.macro.pib_cp[t]-1)),
             rmse_pib_g=rmg('pib','pib'), rmse_pc_g=rmg('pc','pc'), rmse_chom=rm('chomage'), rmse_dette=rm('dette_pib'), rmse_solde=rm('solde_pib'))
    return (res,r,mod,o) if retour else res
def T(rows): return pd.DataFrame(rows).T.round(2).to_string()
