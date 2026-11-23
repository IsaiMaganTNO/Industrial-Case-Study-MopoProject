import pickle, pandas as pd
pd.set_option("display.width",220)
d=pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
for k,v in d.items():
    print(k, type(v).__name__, list(v.columns) if hasattr(v,"columns") else "")
s=d["supply"]; s=s[s.year==2050]
print(s.carrier.unique())
h=s[s.carrier=="hydrogen"]; print(h.groupby(["category",h.energy>0]).energy.sum().div(1e3).round(1))
e=s[s.carrier=="electricity"]; print(e[e.energy<0].groupby("category").energy.sum().div(1e3).round(1))
print(d["co2net"].role.unique()); print(d["co2net"].query("year==2050").groupby(["role","source"]).co2.sum().div(1e3).round(1))
