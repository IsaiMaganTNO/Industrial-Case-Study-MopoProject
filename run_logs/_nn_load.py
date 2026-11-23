import sys, pickle, time
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite")
d=PP.load(r"checkpoints\Investment_Results.3day_nodac_nuc.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\nodac_nuc.pkl","wb")); print("ok", d["obj"].to_dict())
