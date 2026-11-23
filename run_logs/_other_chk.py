import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
e = d["emis"].query("year==2050 and category=='other'"); e = e.assign(c=e.region.str[:2])
t = e.groupby(["c","tech"]).co2.sum()/1e3
print(t[t.abs()>0.3].round(1).to_string())
