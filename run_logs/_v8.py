import sys; sys.path.insert(0,"tools")
import postprocess as PP, pandas as pd
res=r"checkpoints\Investment_Results.3day_vre15.sqlite"
mdl=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
w=PP.load_weights(mdl)
print("wmap days:",len(w))
F=PP.load(res,wmap=w)
import pickle; pickle.dump(F,open(r"run_logs\vre15.pkl","wb"))
print("frames:",sorted(F.keys()))
