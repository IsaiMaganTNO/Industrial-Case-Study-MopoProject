import pickle
for k in ["nb_ccslow_ccu_cap16_dac0", "mr_ccslow_ccu_cap16_dac0"]:
    s = pickle.load(open(rf"run_logs\{k}_NLBE.pkl","rb"))["supply"].query("year==2050 and category=='wind offshore'")
    print(k, round(s.energy.sum()/1e3,1), s.region.unique()[:10])
