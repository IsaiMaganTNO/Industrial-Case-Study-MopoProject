import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
for name,run in [("nb_ccslow_ccu_cap16_dac0","3day_nb_ccslow_ccu_cap16_dac0"),("nb_ctry_ccslow_ccu_cap16_dac0","3day_nb_ctry_ccslow_ccu_cap16_dac0")]:
    wmap=PP.load_weights(rf"runs\{run}\input\Final_SpineOpt_Model.tiny.3day.{name}.sqlite")
    d=PP.load(rf"runs\{run}\output\Investment_Results.3day_{name}.sqlite", wmap=wmap)
    pickle.dump(d,open(rf"run_logs\{name}.pkl","wb")); print("ok",name, d["obj"].to_dict())
for k,v in d.items():
    print(k, type(v).__name__, getattr(v,"shape",""))
