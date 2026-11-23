from lab import *
rows={}
for B,fin in ((2010,2019),(2012,2019),(2014,2019),(2016,2019),(2021,2025)):
    for clos in ('v08','v06'):
        rows[f'{B}-{fin} {clos}']=run(B,fin,clos)
        rows[f'{B}-{fin} {clos} + tendance par heure']=run(B,fin,clos,heures=True)
df=pd.DataFrame(rows).T[['dette','pib','emploi','chomage','pc','rmse_pib_g','rmse_pc_g','rmse_chom','rmse_dette']]
print(df.round(2).to_string())
