import sys, pickle
sys.path.insert(0, "tools"); import postprocess as PP
w = PP.load_weights(r"C:\Users\maganih\Documents\github-repos\Industrial-Case-Study-MopoProject\runs\3day_mr_frlu_v4\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v4.sqlite"); d = PP.load(r"C:\Users\maganih\Documents\github-repos\Industrial-Case-Study-MopoProject\xpress_server_v4\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v4.xpress.sqlite", wmap=w)
pickle.dump(d, open(r"run_logs\frlu_mr_ccslow_ccu_cap16_dac0.pkl", "wb"))
print("obj", d["obj"].to_dict())
