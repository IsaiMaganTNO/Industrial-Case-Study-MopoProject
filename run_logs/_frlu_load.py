import sys, pickle
sys.path.insert(0, "tools"); import postprocess as PP
name = "frlu_mr_ccslow_ccu_cap16_dac0"
inp = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
out = r"xpress_server\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v3.xpress.sqlite"
w = PP.load_weights(inp); d = PP.load(out, wmap=w)
pickle.dump(d, open(rf"run_logs\{name}.pkl", "wb"))
print("obj", d["obj"].to_dict())
print("regions", sorted(d["supply"].region.astype(str).str[:2].unique()))
