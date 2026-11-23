from exp_depenses import *
def info(mod):
    apres(mod)
    w={b:float(mod.hist[b].n[2010]) for b in mod.BR}; W=sum(w.values())
    print('g_prod pondéré %.2f %%/an ; c_emp pondéré %.2f %%/an'%(100*sum(mod.g_prod[b]*w[b] for b in mod.BR)/W, 100*sum(mod.c_emp[b]*w[b] for b in mod.BR)/W))
res,r,mod=run(apres_init=info)
BR=mod.BR; B=2010
wb=sum(mod.hist[b].wb for b in BR); ns=sum(mod.hist[b].ns for b in BR); va=sum(mod.hist[b].va_cp for b in BR); q=sum(mod.hist[b].q for b in BR)
cn_obs=wb/ns; pva_obs=va/q
T=pd.DataFrame({'salaire sim/obs %':100*(r.salaire/r.salaire[2011]*(cn_obs[2011]/cn_obs[B])/(cn_obs/cn_obs[B])-1) if False else np.nan},index=range(2011,2020))
ws=r.salaire; ps=r.pva_m
# raccord à l'origine : indice simulé / indice observé
idx=lambda s,o: (s/s.loc[2011])*(o[2011]/o[B])
T=pd.DataFrame({'salaire nominal (err %)':100*(idx(ws,cn_obs)/(cn_obs/cn_obs[B])-1),
                'prix VA marchande (err %)':100*(idx(ps,pva_obs)/(pva_obs/pva_obs[B])-1),
                'prix conso (err %)':100*(r.pc/mod.macro.p_c-1)}).loc[2011:2019]
T['coût réel cn/pva (err %)']=100*((1+T.iloc[:,0]/100)/(1+T.iloc[:,1]/100)-1)
T['coût réel obs (indice 2010=100)']=100*(cn_obs/pva_obs/(cn_obs[B]/pva_obs[B])).loc[2011:2019]
print(T.round(2).to_string())
print('\nNB : le salaire simulé de 2011 est raccordé à l\'observé 2011 (approximation du raccord) ; les erreurs 2011 valent 0 par construction.')
