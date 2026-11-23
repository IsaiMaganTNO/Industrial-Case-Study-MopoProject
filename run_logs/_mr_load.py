import sys, os, pickle, time
sys.path.insert(0,"tools")
import postprocess as PP
t=time.time()
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
print("wmap days:",len(wmap) if wmap else None, wmap)
d=PP.load(r"checkpoints\Investment_Results.3day_mixedres.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\mixedres.pkl","wb"))
print("frames:",{k:(v.shape if hasattr(v,"shape") else type(v).__name__) for k,v in d.items()})
print("%.1f min"%((time.time()-t)/60))
