import sys, pathlib, pickle, time
R=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'src'),str(R),str(R/'phase31')]
import backtest as BT
t0=time.time()
mod,ex,ans=BT.construire(2010,2019,0.2,0.0,0.75,'production')
r=mod.simuler(ans,ex)
print('t',time.time()-t0, type(r))
print([c for c in (r.columns if hasattr(r,'columns') else dir(r)) if not c.startswith('_')][:80])
pickle.dump((r,), open('v08_2010.pkl','wb'))
