from lab import *
rows={}
for B in (2010,2012,2014,2016):
    rows[f'{B} v08']=run(B)
    rows[f'{B} v08 + ARE sans double compte']=run(B,exp={'chom_ref':chom_obs})
print(T(rows))
