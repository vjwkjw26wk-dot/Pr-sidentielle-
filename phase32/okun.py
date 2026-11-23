from lab import *
for B in (2010,2012):
  for h in (False,True):
    res,r,mod,o=run(B,2019,'v08',heures=h,retour=True)
    mode,rho,a,th=CLOS['v08']; _,ex,ans=BT.construire(B,2019,rho,a,th,mode)
    us=pd.Series({t:float(ex.chomage_structurel[t]) for t in ans})
    gap=r.ecart_production.loc[list(ans)]; ug=(r.chomage.loc[list(ans)]-us)
    inc=(gap+1.5*ug)
    print(f'origine {B} {"tendance/heure" if h else "référence    "} : écart prod. moyen {gap.mean():+.2f} ; −1,5×écart chômage moyen {(-1.5*ug).mean():+.2f} ; incohérence moyenne {inc.mean():+.2f} (max {inc.abs().max():.2f})')
