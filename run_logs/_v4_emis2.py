import pickle, pandas as pd
R={"MR":"mr_ccslow_ccu_cap16_dac0","V4":"frlu_mr_ccslow_ccu_cap16_dac0"}
x={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["emis"].query("year==2050 and category=='other'") for k,v in R.items()}
t=pd.concat({k:(v[v.region.astype(str).str[:2]=="NL"].groupby("tech").co2.sum()/1e3) for k,v in x.items()},axis=1).fillna(0).round(1)
print(t[(t.abs()>0.3).any(axis=1)])
