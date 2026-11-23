import pickle
for k in ["mr_fix","mr_ccslow","mr_fix_NLBE","mr_ccslow_NLBE"]:
  d=pickle.load(open(rf"run_logs\{k}.pkl","rb"))
  print(f"{k:16s} obj {d['obj'].sum():>12,.0f}  net CO2",(d["emis"].groupby("year").co2.sum()/1e3).round(1).to_dict()," stored",(d["co2store"].groupby("year").co2.sum()/1e3).round(1).to_dict())
for k in ["mr_fix","mr_ccslow"]:
  d=pickle.load(open(rf"run_logs\{k}.pkl","rb")); e=d["emis"]; s=d["co2store"]
  print(k, "cols", list(e.columns), list(s.columns))
  for c in ["country","region"]:
    if c in e.columns: print((e.groupby([c,"year"]).co2.sum()/1e3).round(1).unstack()); break
  for c in ["country","region","site"]:
    if c in s.columns: print((s.groupby([c,"year"]).co2.sum()/1e3).round(2).unstack()); break
