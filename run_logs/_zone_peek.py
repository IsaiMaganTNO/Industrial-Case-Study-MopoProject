import pickle
d = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
s = d["supply"].query("year==2050 and carrier=='electricity'")
print((s.groupby(["category","region"]).energy.sum()/1e3).round(1).to_string())
