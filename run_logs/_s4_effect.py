import pickle, pandas as pd
R={"MR":"mr_ccslow_ccu_cap16_dac0","S4":"frlu_mr_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
pd.set_option("display.width",200)
for y in (2030,2040,2050):
  print("== year",y)
  p=pd.concat({k:d["prod"][d["prod"].year==y].groupby(["sector","cc"]).output.sum() for k,d in D.items()},axis=1).fillna(0).round(0); print(p)
  s=pd.concat({k:d["supply"][(d["supply"].year==y)&(d["supply"].carrier.str.contains("elec"))].groupby("category").energy.sum()/1e3 for k,d in D.items()},axis=1).fillna(0).round(1); print(s[(s.abs()>0.5).any(axis=1)])
  c=pd.concat({k:d["co2net"][(d["co2net"].year==y)].groupby("role").co2.sum() for k,d in D.items()},axis=1).round(0); print(c)
  e=pd.concat({k:pd.Series({"emis":d["emis"][d["emis"].year==y].co2.sum()}) for k,d in D.items()},axis=1).round(0); print(e)
