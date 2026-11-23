import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
s = d["supply"].query("year==2050"); s = s.assign(c=s.region.fillna("??").str[:2])
for car in ["hydrogen","electricity"]:
    x = s[s.carrier==car]
    print(car); print((x.groupby(["c","category"]).energy.sum()/1e3).round(1)[lambda v: v.abs()>.5].to_string())
h = s[(s.carrier=="hydrogen") & (s.c.isin(["NL","BE","??"]))]
print((h.groupby(["c","tech"]).energy.sum()/1e3).round(1)[lambda v: v.abs()>.5].to_string())
n = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))["supply"].query("year==2050")
print("NLBE cache H2:", (n[n.carrier=="hydrogen"].groupby(["category","tech"]).energy.sum()/1e3).round(1)[lambda v: v.abs()>.5].to_dict())
print("NLBE cache elec:", (n[n.carrier=="electricity"].groupby("category").energy.sum()/1e3).round(1).to_dict())
