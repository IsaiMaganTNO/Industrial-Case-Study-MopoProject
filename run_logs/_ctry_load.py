import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
wmap=PP.load_weights(r"runs\3day_nb_ctry\input\Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite")
d=PP.load(r"runs\3day_nb_ctry\output\Investment_Results.3day_nb_ctry.sqlite", wmap=wmap)
pickle.dump(d,open(r"run_logs\nb_ctry.pkl","wb")); print("ok", d["obj"].to_dict())
for k,v in d.items():
  print(k, type(v).__name__, getattr(v,"shape",""))
