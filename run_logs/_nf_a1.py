import pickle,pandas as pd
pd.set_option("display.width",250)
A=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"));B=pickle.load(open(r"run_logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
def sup(d,car):
  s=nb(d["supply"]);s=s[(s.carrier==car)&(s.energy>0)];return s.groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3
for car in ["electricity","methane","hydrogen"]:
  df=pd.concat([sup(A,car),sup(B,car)],axis=1,keys=["old","fix"]).fillna(0);df=df[(df>3).any(axis=1)].round(1)
  print("==",car);print(df.to_string());print("TOTAL",df.sum().round(1).to_dict())
for n,d in [("old",A),("fix",B)]:
  s=d["co2store"];print(n,"STORE",(s.groupby(["reservoir","year"]).co2.sum()/1e3).round(1).to_dict())
  print(n,"EMIS",(d["emis"].groupby("year").co2.sum()/1e3).round(1).to_dict())
  f=d["fleet"];x=f[f.tech=="nuclear-3"];print(n,"NUC",x.assign(c=x.region.astype(str).str[:2]).groupby(["c","year"]).units.sum().round(2).to_dict())
  p=nb(d["prod"])
  for s in ["steel (primary)","olefins","ammonia","cement"]:
    q=p[p.sector==s].groupby(["tech","year"]).output.sum().unstack().fillna(0);print(n,s,(q/q.sum()*100).round(0).to_dict())

