import pickle, pandas as pd
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
f=A["fleet"]; f=f[f.year==2050].copy(); f["ctry"]=f.region.str[:2]
off=f[f.tech.astype(str).str.contains("wind-off")]
print("2050 offshore GW by country:"); print(off.groupby("ctry").units.sum().round(2).to_string())
print("\n2050 offshore GW by site:")
print(off.groupby("tech").units.sum().round(2).to_string())
# demand proxy: electricity supply by region country
s=A["supply"]; s=s[(s.year==2050)&(s.carrier.str.contains("electric",case=False,na=False))].copy()
s["ctry"]=s.region.str[:2]
print("\n2050 elec supply TWh by country:"); print((s.groupby("ctry").energy.sum()/1e3).round(1).to_string())
