import pickle
d=pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb")); print(d["emis"].columns.tolist()); print(d["emis"].head(3).to_string())
e=d["emis"]; print((e.assign(c=e.region.astype(str).str[:2]).groupby(["year","c"]).co2.sum()/1e3).round(1).to_string())
print(d["supply"].query("carrier=='electricity'").category.unique())
