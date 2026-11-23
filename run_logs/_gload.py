import sys, os
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
print("wmap days:",len(wmap) if wmap else None)
d=PP.load(r"checkpoints\Investment_Results.3day_gascap.sqlite", wmap=wmap)
import pickle
pickle.dump(d,open(r"run_logs\gascap.pkl","wb"))
print("frames:",{k:(v.shape if hasattr(v,"shape") else type(v).__name__) for k,v in d.items()})
