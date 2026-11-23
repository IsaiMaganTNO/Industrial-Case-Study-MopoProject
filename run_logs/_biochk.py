import pickle
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccslow_dac0"]:
    X=pickle.load(open(rf"run_logs\{n}_xbbio.pkl","rb"))
    b=X["bio"]; print(n,(b.groupby(["c","year"]).v.sum()/1e3).round(1).to_dict()); print(b.query("year==2050").groupby("unit").v.sum().sort_values().tail(6).div(1e3).round(1).to_dict())
