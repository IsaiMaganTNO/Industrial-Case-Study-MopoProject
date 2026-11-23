import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
n="mr_ccslow_ccu_cap16_dac0"
wmap=PP.load_weights(rf"checkpoints\Final_SpineOpt_Model.tiny.3day.{n}.sqlite")
d=PP.load(rf"checkpoints\Investment_Results.3day_{n}.sqlite", wmap=wmap)
pickle.dump(d,open(rf"run_logs\{n}.pkl","wb")); print("ok", round(d["obj"].sum()))
