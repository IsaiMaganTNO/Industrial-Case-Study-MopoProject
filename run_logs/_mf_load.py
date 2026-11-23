import sys, pickle, time
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
d=PP.load(r"checkpoints\Investment_Results.3day_mr_fix.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\mr_fix.pkl","wb")); print("ok", d["obj"].to_dict())
