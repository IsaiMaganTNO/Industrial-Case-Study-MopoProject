import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
R = r"runs\rp10_mr_noblend"
name = "rp10nb_mr_ccslow_ccu_cap16_dac0"
wmap = PP.load_weights(rf"{R}\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite")
print("weights", len(wmap) if hasattr(wmap, "__len__") else wmap)
d = PP.load(rf"{R}\output\Investment_Results.10day_noblend_mr_ccslow_ccu_cap16_dac0.sqlite", wmap=wmap)
pickle.dump(d, open(rf"run_logs\{name}.pkl", "wb"))
print("NEW obj", d["obj"].to_dict())
o = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl", "rb"))
print("3DAY obj", o["obj"].to_dict())
