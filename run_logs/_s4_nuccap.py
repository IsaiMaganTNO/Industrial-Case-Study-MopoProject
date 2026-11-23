import pickle
for k in ["mr_ccslow_ccu_cap16_dac0","frlu_mr_ccslow_ccu_cap16_dac0"]:
  d=pickle.load(open(rf"run_logs\{k}.pkl","rb")); f=d["fleet"]; f=f[f.tech=="nuclear-3"]
  print(k, f.groupby("year").units.sum().round(1).to_dict(), f[f.year==2050].groupby(f.region.astype(str).str[:2]).units.sum().round(1).to_dict())
  s=d["supply"]; print("  LNG 2050 TWh", round(s[(s.year==2050)&(s.tech=="LNG-terminal")].energy.sum()/1e3,1))
