import pickle
for k in ["nb_v2","nb_ctry","nb_ccslow","nb_ctry_ccslow"]:
  d=pickle.load(open(rf"run_logs\{k}.pkl","rb"))
  print(f"{k:16s} obj {d['obj'].sum():>12,.0f}  net CO2",(d["emis"].groupby("year").co2.sum()/1e3).round(1).to_dict()," stored",(d["co2store"].groupby("year").co2.sum()/1e3).round(1).to_dict())
