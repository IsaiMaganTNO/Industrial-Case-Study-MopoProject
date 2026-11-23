import pickle, pandas as pd
for k in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0"]:
    d = pickle.load(open(rf"run_logs\{k}_NLBE.pkl","rb"))
    s = d["supply"].query("year==2050")
    print(k); print(s.groupby(["carrier","category"]).energy.sum().round(1).to_string())
