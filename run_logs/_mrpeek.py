import pickle
d=pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
s=d["supply"].query("year==2050 and energy>0")
for c in ["hydrogen","methane","heat"]: print(c,(s[s.carrier==c].groupby("tech").energy.sum()/1e3).round(1).loc[lambda z:z>0.5].to_dict())
print(sorted(d["prod"].sector.unique()))
print(d["co2store"].region.unique())
