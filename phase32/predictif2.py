from lab import *
def prol(s, B, n=5, mode='g'):
    s=s.copy().astype(float)
    if mode=='fige':
        for t in s.index:
            if t>B: s[t]=s[B]
        return s
    g=float(np.log(s[B]/s[B-n])/n)
    for t in s.index:
        if t>B: s[t]=s[B]*np.exp(g*(t-B))
    return s
def exante(*quoi):
    def f(mod,ex):
        B=mod.B
        if 'budget' in quoi:
            ex.conso_publique=prol(ex.conso_publique,B); ex.prestations_volume=prol(ex.prestations_volume,B)
            ex.autres_depenses_pib=prol(ex.autres_depenses_pib,B,mode='fige')
        if 'invest' in quoi: ex.autres_investissements=prol(ex.autres_investissements,B)
        if 'monde' in quoi:
            ex.demande_mondiale=prol(ex.demande_mondiale,B); ex.prix_mondial=prol(ex.prix_mondial,B)
            pi=ex.prix_import.copy(); pm=mod.macro.p_m
            g=float(np.log(pm[B]/pm[B-5])/5)    # prix d'importation agrégé, tendance 5 ans avant l'origine
            for t in pi.index:
                if t>B: pi.loc[t]=pi.loc[B]*np.exp(g*(t-B))
            ex.prix_import=pi
        if 'taux' in quoi: ex.taux_long=prol(ex.taux_long,B,mode='fige')
        if 'popact' in quoi: ex.population_active=prol(ex.population_active,B)
    return f
V={'0 conditionnel (référence)':dict(),
   '1 taux de prélèvement figés':dict(construire_kw={'politiques':False}),
   '2 dépenses (conso. pub., prestations, autres) ex ante':dict(ex_mod=exante('budget')),
   '3 investissements autres ex ante':dict(ex_mod=exante('invest')),
   '4 environnement mondial (demande, prix, prix import) ex ante':dict(ex_mod=exante('monde')),
   '5 taux long figé':dict(ex_mod=exante('taux')),
   '6 population active ex ante':dict(ex_mod=exante('popact')),
   '7 TOUT ex ante (prévision réelle)':dict(construire_kw={'politiques':False},ex_mod=exante('budget','invest','monde','taux','popact'))}
rows={}
for B,fin in ((2010,2019),(2012,2019),(2014,2019),(2021,2025)):
  for k in [x for x in V if x[0] in '47']:
    rows[f'{B} {k}']=run(B,fin,**V[k])
for B,fin in ():
    for k,v in V.items():
        try: rows[f'{B} {k}']=run(B,fin,**v)
        except Exception as e: print('échec',B,k,e)
df=pd.DataFrame(rows).T[['dette','solde','pib','emploi','chomage','pc','rmse_pib_g','rmse_pc_g','rmse_chom','rmse_dette']]
print(df.round(2).to_string()); df.to_csv('predictif.csv')
