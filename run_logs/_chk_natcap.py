import pickle,pandas as pd
CN=["NL","BE"]
for k in ["mr_ccslow_ccu_cap16_dac0","ctryco2B_mr_ccslow_ccu_cap16_dac0"]:
  F=pickle.load(open(rf"run_logs\{k}.pkl","rb")); D=pickle.load(open(rf"run_logs\{k}_NLBE.pkl","rb"))
  e=F["emis"].query("year==2050"); c=e.region.astype(str).str[:2]
  print("==",k); print((e.groupby(c).co2.sum()/1e3).round(2).to_dict())
  print(" NLBE emis by category:",(D["emis"].query("year==2050").groupby("category").co2.sum()/1e3).round(2).loc[lambda s:s.abs()>.5].to_dict())
  p=F["co2pipe"].query("year==2050"); print(" pipes from NLBE:",(p[p.origin.str[:2].isin(CN)&~p.dest.str[:2].isin(CN)].groupby(["origin","dest"]).co2.sum()/1e3).round(2).to_dict())
  x=F["emis"]; print(" techs in emis with 'credit' or 'import':", x[x.tech.str.contains("credit|import|export",case=False)].tech.unique()[:10])
