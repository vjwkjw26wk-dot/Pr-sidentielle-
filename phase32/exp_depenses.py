from exp import *
import json
from telechargement import jsonstat_dict
B=2010
def obs_idx(mod):
    em=mod.emp; a=mod.apu
    nm=em.emploi-sum(mod.hist[b].n for b in mod.BR)
    wmk=pd.Series({t:sum(mod.hist[b].wb[t] for b in mod.BR)/sum(mod.hist[b].ns[t] for b in mod.BR) for t in range(1999,2020)})
    wpub=a.d1pay/nm
    return nm, wmk, wpub
ST={}
def init(mod):
    nm,wmk,wpub=obs_idx(mod); ST.update(nm=nm,wmk=wmk,wpub=wpub,B=mod.B)
    # productivité non marchande « en temps réel » : moyenne des 8 années avant l'origine (même règle que g_prod marchand)
    q=sum(mod.hist[b].q for b in mod.BR)  # placeholder non utilisé
nm_rt={}
def g_nm_tempsreel(Bo):
    L=lambda f: pd.Series(jsonstat_dict(json.loads((R/'data/raw'/f).read_text())))
    va=L('eurostat_nama_10_a64_FR.json'); e=L('eurostat_nama_10_a64_e_FR.json')
    q=sum(pd.Series({int(t):v for (u,b,i,t),v in va.items() if u=='CLV15_MEUR' and b==bb and i=='B1G'}) for bb in ['O-Q','L'])
    n=sum(pd.Series({int(t):v for (u,b,i,t),v in e.items() if u=='THS_PER' and b==bb and i=='EMP_DC'}) for bb in ['O-Q','L'])
    p=np.log(q/n); return float((p[Bo]-p[Bo-8])/8)
gnm=g_nm_tempsreel(B); print('productivité non marchande en temps réel (2002-2010) : %.2f %%/an'%(100*gnm))
nm_oracle=lambda self,t,q,n: self.n_nm0*float(ST['nm'][t]/ST['nm'][self.B])
nm_trend=lambda self,t,q,n: n*np.exp(-gnm*(t-self.B))
wpub=lambda t: float((ST['wpub'][t]/ST['wpub'][B])/(ST['wmk'][t]/ST['wmk'][B]))
# taux d'émission : moyenne courbe (taux court zone euro et taux long)
L=lambda f: pd.Series(jsonstat_dict(json.loads((R/'data/raw'/f).read_text())))
st=L('eurostat_irt_st_a_EA.json'); print('clés taux court', list(st.items())[:2])
stv={int(k):v for k,v in st.items()}
def ex_long(mod):
    return {t: max(float(mod.macro.taux_long[t]),0)/100 for t in range(1990,2026) if t in mod.macro.taux_long.index}
TL={}
def apres(mod): init(mod); TL.update(ex_long(mod))
mix=lambda t: 0.5*TL[t]+0.5*max(stv[t],0)/100
rows={}
rows['v08 (réf.)']=run(apres_init=apres)[0]
rows['E1a emploi NM observé [oracle]']=run(exp={'n_nm':nm_oracle},apres_init=apres)[0]
rows['E1b emploi NM, productivité temps réel']=run(exp={'n_nm':nm_trend},apres_init=apres)[0]
rows['E2 salaire public observé [politique]']=run(exp={'wpub':wpub},apres_init=apres)[0]
rows['E3a renouvellement 1/6']=run(exp={'renouv':6},apres_init=apres)[0]
rows['E3b émission moitié court/long']=run(exp={'taux_emission':mix},apres_init=apres)[0]
rows['E3c 1/6 + émission mixte']=run(exp={'renouv':6,'taux_emission':mix},apres_init=apres)[0]
rows['E1b+E2']=run(exp={'n_nm':nm_trend,'wpub':wpub},apres_init=apres)[0]
rows['E1b+E2+E3c']=run(exp={'n_nm':nm_trend,'wpub':wpub,'renouv':6,'taux_emission':mix},apres_init=apres)[0]
rows['E1a+E2+E3c [oracle NM]']=run(exp={'n_nm':nm_oracle,'wpub':wpub,'renouv':6,'taux_emission':mix},apres_init=apres)[0]
print(table(rows))
json.dump(rows,open('res_depenses_2010.json','w'),indent=1)
