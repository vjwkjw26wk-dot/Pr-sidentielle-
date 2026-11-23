import sys, pathlib, json
import numpy as np, pandas as pd
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'src')]
from telechargement import jsonstat_dict
import m7_series as S
L=lambda f: pd.Series(jsonstat_dict(json.loads((R/'data/raw'/f).read_text())))
va=L('eurostat_nama_10_a64_FR.json'); e=L('eurostat_nama_10_a64_e_FR.json')
def ser(s,u,b,i): return pd.Series({int(t):v for (uu,bb,ii,t),v in s.items() if uu==u and bb==b and ii==i}).sort_index()
def agr(bs,u,i,s): return sum(ser(s,u,b,i) for b in bs)
# volume chaîné : approximation par somme des CLV (suffisant pour tendances)
mk=S.BRANCHES
q_mk=agr(mk,'CLV15_MEUR','B1G',va); n_mk=agr(mk,'THS_PER','EMP_DC',e); h_mk=agr(mk,'THS_HW','EMP_DC',e)
q_nm=agr(['O-Q','L'],'CLV15_MEUR','B1G',va); n_nm=agr(['O-Q','L'],'THS_PER','EMP_DC',e); h_nm=agr(['O-Q','L'],'THS_HW','EMP_DC',e)
def g(x,a,b): return 100*np.log(x[b]/x[a])/(b-a)
print('Croissance annuelle moyenne (%)        2003-2010  2010-2019')
for nom,x in [('VA marchande',q_mk),('emploi marchand (pers.)',n_mk),('heures marchandes',h_mk),('productivité/tête marchande',q_mk/n_mk),('productivité/heure marchande',q_mk/h_mk),('heures par tête marchand',h_mk/n_mk),
              ('VA non marchande (O-Q,L)',q_nm),('emploi non marchand',n_nm),('productivité/tête non marchande',q_nm/n_nm)]:
    print(f'{nom:38s} {g(x,2002,2010):8.2f}  {g(x,2010,2019):8.2f}')
