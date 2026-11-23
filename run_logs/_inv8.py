import pickle,pandas as pd
pd.set_option("display.width",250)
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
for pat in ["nuclear","PEM","REF-SMR","methanation","wind-off","battery","CCGT","heatpump|gas-boiler"]:
  f=lambda d:d["fleet"][d["fleet"].tech.str.contains(pat)].groupby(["region","year"]).units.sum().unstack()
  df=pd.concat({"SA":f(A),"CL":f(B)},axis=1).fillna(0).round(2)
  print("==",pat); print(df[(df.abs()>0.01).any(axis=1)].to_string())
print("investment cost proxy:"); 
for n,d in (("SA",A),("CL",B)): print(n,d["obj"].round(0).to_dict() if "obj" in d else "")
