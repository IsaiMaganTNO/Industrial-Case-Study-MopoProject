import pickle
for k in ["nb_ccslow_ccu_cap16_dac0", "mr_ccslow_ccu_cap16_dac0"]:
    d = pickle.load(open(rf"run_logs\{k}.pkl","rb"))
    e = d["emis"].query("year==2050"); print(k, e.groupby(e.region.str[:2]).co2.sum().round(0).to_dict())
    print(d["co2store"].query("year==2050").groupby("region").co2.sum().round(0).to_dict())
    n = d["co2net"].query("year==2050"); print(n.groupby("role").co2.sum().round(0).to_dict())
