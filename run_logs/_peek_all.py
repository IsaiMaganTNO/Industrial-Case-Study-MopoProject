import pickle,os
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0","mr_ccsopt_ccu_dac0","ctryco2B_mr_ccslow_ccu_cap16_dac0"]:
  for s in ["","_NLBE","_xbbio"]: print(n+s, os.path.exists(rf"run_logs\{n}{s}.pkl"))
for f in ["_hc_supply_all","_use_elec_h2_all","_elec_dem_xb_all"]:
  d=pickle.load(open(rf"run_logs\{f}.pkl","rb")); print("==",f,type(d), list(d)[:10] if isinstance(d,dict) else "")
  if isinstance(d,dict):
    v=d[list(d)[0]]; print(type(v)); print(v.head(8) if hasattr(v,"head") else list(v.items())[:8] if isinstance(v,dict) else v)
  else: print(d.head(10) if hasattr(d,"head") else d)
