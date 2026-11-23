import pickle
for k in ["nb_ccslow_ccu_cap16_dac0", "mr_ccslow_ccu_cap16_dac0"]:
    d = pickle.load(open(rf"run_logs\{k}_NLBE.pkl","rb"))["supply"].query("year==2050")
    h = d[d.carrier=="heat"]; print(k, "HEAT", (h.groupby(["category","tech"]).energy.sum()/1e3).round(1)[lambda s: s.abs()>.3].to_dict())
    e = d[(d.carrier=="hydrogen") & (d.category=="electrolysis")]; print(k, "ELY", (e.groupby("region").energy.sum()/1e3).round(1).to_dict())
    print(k, "heat regions", h.region.nunique(), h.region.unique()[:5])
