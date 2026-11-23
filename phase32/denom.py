from exp_depenses import *
# décomposition de l'écart de dette 2019 : numérateur (M€) vs dénominateur (PIB nominal)
for nom,e in [('v08',{}),('E1b+E2',{'n_nm':nm_trend,'wpub':wpub}),('E1b+E2+E3c',{'n_nm':nm_trend,'wpub':wpub,'renouv':6,'taux_emission':mix})]:
    _,r,mod=run(exp=e,apres_init=apres)
    D_s,D_o=float(r.dette[2019]),float(mod.apu.dette[2019]); Y_s,Y_o=float(r.pib_nominal[2019]),float(mod.macro.pib_cp[2019])
    tot=D_s/Y_s*100-D_o/Y_o*100; num=(D_s-D_o)/Y_o*100; den=tot-num
    print(f'{nom:12s} écart total {tot:5.1f} pts = dette en M€ trop élevée {num:5.1f} pts + PIB nominal trop bas {den:5.1f} pts ; dette sim/obs {100*(D_s/D_o-1):+.1f} %, PIB nominal {100*(Y_s/Y_o-1):+.1f} %')
