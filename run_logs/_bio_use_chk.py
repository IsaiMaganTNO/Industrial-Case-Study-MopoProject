import pickle
for k in ["nb_ccslow_ccu_cap16_dac0", "mr_ccslow_ccu_cap16_dac0"]:
    b = pickle.load(open(rf"run_logs\{k}_xbbio.pkl","rb"))["bio"].query("year==2050")
    print(k, len(b), b.duplicated().sum())
    print((b.groupby("c").v.sum()/1e3).round(1).to_dict())
    print((b.groupby(b.unit.str.replace(r"_[A-Z]{2}[A-Z0-9]*$","",regex=True)).v.sum()/1e3).round(1).sort_values(ascending=False).head(8).to_dict())
