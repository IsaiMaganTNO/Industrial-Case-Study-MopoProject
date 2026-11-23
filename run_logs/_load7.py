import sys
sys.path.insert(0,"tools")
import postprocess as PP
modeldb=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
res=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
w=PP.load_weights(modeldb)
print("weights loaded:",len(w) if hasattr(w,"__len__") else w)
import pickle
d=PP.load(res,wmap=w)
pickle.dump(d,open(r"run_logs\hcco2_7day.pkl","wb"))
print("OK cached")
