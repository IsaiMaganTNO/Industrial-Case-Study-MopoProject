import pickle,pandas as pd
m=pickle.load(open(r"run_logs\mixedres.pkl","rb"));v=pickle.load(open(r"run_logs\vre15.pkl","rb"))
print("OBJ mixed\n",m["obj"],"\nOBJ vre15\n",v["obj"])
nb=lambda df:df[df.region.astype(str).str.match(r"(BE|NL)C")]
for k in ["prod"]:
  a=nb(m[k]).groupby(["sector","year"]).output.sum().unstack();b=nb(v[k]).groupby(["sector","year"]).output.sum().unstack()
  print((a-b).round(1).loc[lambda x:(x.abs()>0.5).any(axis=1)])
for car in ["H2","hydrogen"]:
  for n,d in [("mix",m),("v15",v)]:
    s=nb(d["supply"]);s=s[s.carrier.astype(str).str.contains(car,case=False)]
    if len(s):print(n,car,s.groupby(["tech","year"]).energy.sum().unstack().round(1).loc[lambda x:x.abs().sum(axis=1)>1])
a=nb(m["inv"]).groupby(["tech"]).units.sum();b=nb(v["inv"]).groupby(["tech"]).units.sum()
df=pd.concat([a,b],axis=1,keys=["mix","v15"]).fillna(0);df["d"]=df.mix-df.v15
print(df[df.d.abs()>0.5].sort_values("d").to_string())
print(m["atm"],v["atm"])
