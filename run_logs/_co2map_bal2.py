import pickle
for v in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccslow_ccu_cap16_dac0"]:
    F=pickle.load(open(rf"run_logs\{v}.pkl","rb"))
    c=F["co2net"];c=c[(c.year==2050)&(c.role!="captured")]
    print(v, c.groupby(["region",c.tech.str[:12]]).co2.sum().div(1e3).round(2).to_dict())
    print(" store",F["co2store"].query("year==2050").groupby(["reservoir","region"]).co2.sum().div(1e3).round(2).to_dict())
    print(" pipe",F["co2pipe"].query("year==2050").groupby(["origin","dest"]).co2.sum().div(1e3).round(2).to_dict())
    p=F["prod"]; print(" prod cols",list(p.columns)); print(p.head(3).to_string())
    print(sorted(p.sector.unique()))
