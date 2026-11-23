"""Expériences isolées de la phase 3.2 (copie du modèle dans exp_src, v0.8 inchangée)."""
import sys, pathlib, json
import numpy as np, pandas as pd
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(pathlib.Path(__file__).resolve().parent/'exp_src'),str(R/'src'),str(R),str(R/'phase31')]
import m8_modele as M
import backtest as BT
assert 'exp_src' in M.__file__, M.__file__
import m7_equations as E

def run(B=2010, fin=2019, exp=None, rho=0.2, a=0.0, theta=0.75, mode='production', avant_init=None, apres_init=None, ex_mod=None):
    M.EXP.clear(); M.EXP.update(exp or {})
    sig0=E.SIGMA_TRAVAIL
    if avant_init: avant_init()
    mod,ex,ans=BT.construire(B,fin,rho,a,theta,mode)
    if apres_init: apres_init(mod)
    if ex_mod: ex_mod(mod,ex)
    r=mod.simuler(ans,ex)
    E.SIGMA_TRAVAIL=sig0
    o=BT.observe(mod)
    em=mod.emp
    nm_obs=em.emploi-sum(mod.hist[b].n for b in mod.BR)
    t=fin
    res=dict(dette=float(r.dette_pib[t]-o['dette_pib'][t]), solde=float(r.solde_pib[t]-o['solde_pib'][t]),
             depenses=float(r.depenses[t]/r.pib_nominal[t]*100-o['depenses_pib'][t]),
             pib=float(100*(r.pib[t]/o['pib'][t]/(r.pib.get(B,o['pib'][B])/o['pib'][B])-1)) if False else float(100*(r.pib[t]/o['pib'][t]-1)),
             pibn=float(100*(r.pib_nominal[t]/o['pib'][t]/mod.macro.p_pib[t]*1-1)) if False else float(100*(r.pib_nominal[t]/mod.macro.pib_cp[t]-1)),
             emploi=float(100*(r.emploi[t]/em.emploi[t]-1)), chomage=float(r.chomage[t]-o['chomage'][t]),
             pc=float(100*(r.pc[t]/o['pc'][t]-1)), interets=float(r.interets[t]/r.pib_nominal[t]*100-mod.apu.d41pay[t]/mod.macro.pib_cp[t]*100),
             taux_app=float(r.taux_apparent[t]-mod.apu.d41pay[t]/mod.apu.dette[t-1]*100))
    rmse=lambda k: float(np.sqrt(np.mean([(r[k][y]-o[{'dette_pib':'dette_pib','chomage':'chomage'}[k]][y])**2 for y in ans])))
    res['rmse_dette']=rmse('dette_pib'); res['rmse_chomage']=rmse('chomage')
    return res, r, mod

def table(rows):
    df=pd.DataFrame(rows).T
    return df.round(2).to_string()

if __name__=='__main__':
    base,_,_=run()
    print(table({'v08 (réf.)':base}))
