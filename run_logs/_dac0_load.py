import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"runs\3day_mr_ccslow_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_dac0.sqlite")
d=PP.load(r"runs\3day_mr_ccslow_dac0\output\Investment_Results.3day_mr_ccslow_dac0.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\mr_ccslow_dac0.pkl","wb")); print("ok", d["obj"].to_dict())
for k,v in d.items():
  print(k, type(v).__name__, getattr(v,"shape",""))

