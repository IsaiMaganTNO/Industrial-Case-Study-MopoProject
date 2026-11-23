import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
e = d["emis"].query("year==2050"); e = e.assign(c=e.region.str[:2])
inj = e.tech.str.startswith("CO2-injection")
print("stored credit by country (Mt):", (e[inj].groupby("c").co2.sum()/1e3).round(1).to_dict())
print("all other emissions by country (Mt):", (e[~inj].groupby("c").co2.sum()/1e3).round(1).to_dict())
print("six-country sum:", round(e.co2.sum()/1e3, 1))
print((e[~inj].groupby(["c","category"]).co2.sum()/1e3).round(1).loc[["NL","BE"]].to_string())
