import pickle
for n in ["nodac","nodac_nuc"]:
  d=pickle.load(open(rf"run_logs\{n}.pkl","rb"));f=d["fleet"]
  x=f[f.tech=="nuclear-3"];x=x.assign(c=x.region.astype(str).str[:2]).groupby(["c","year"]).units.sum().round(2)
  print(n,"nuclear GW",x.to_dict())
  e=d["co2net"];e=e[e.region.astype(str).str.match(r"^(BE|NL)C")]
  print(n,"co2net roles 2050",(e[e.year==2050].groupby(["role","source"]).co2.sum()/1e3).round(1).to_dict())
