import pickle
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccslow_ccu_cap16_dac0"]:
    d=pickle.load(open(rf"run_logs\{n}.pkl","rb")); p=d["co2pipe"]; print("==",n,len(p)); print(p.query("year==2050").groupby(["origin","dest"]).co2.sum().div(1e3).round(2).loc[lambda z:z>0.05].to_string())
    print(d["co2store"].query("year==2050").groupby(["reservoir","injector","region"]).co2.sum().div(1e3).round(2).to_string())
