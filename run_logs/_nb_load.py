import sys, pickle, time
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
d=PP.load(r"checkpoints\Investment_Results.3day_nb_v2.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\nb_v2.pkl","wb")); print("ok", d["obj"].to_dict())

