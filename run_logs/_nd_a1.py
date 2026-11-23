import pickle,pandas as pd,re
N=pickle.load(open(r"run_logs\nodac.pkl","rb"));V=pickle.load(open(r"run_logs\vre15.pkl","rb"))
NB=r"^(BE|NL)C\d"
nb=lambda df:df[df.region.astype(str).str.match(NB)]
def T(d,car):
  s=nb(d["supply"]);s=s[(s.carrier==car)&(s.energy>0)];return s.groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3
for car in ["electricity","methane","hydrogen"]:
  a,b=T(V,car),T(N,car);df=pd.concat([a,b],axis=1,keys=["v15","nodac"]).fillna(0)
  df=df[(df.abs()>1).any(axis=1)].round(1);print("\n==",car);print(df.to_string());print("TOTAL",df.sum().round(1).to_dict())
a=nb(V["inv"]).groupby("tech").units.sum();b=nb(N["inv"]).groupby("tech").units.sum()
df=pd.concat([a,b],axis=1,keys=["v15","nodac"]).fillna(0);df["d"]=df.nodac-df.v15
print("\n== INV delta");print(df[df.d.abs()>.3].sort_values("d").round(2).to_string())
for n,d in [("v15",V),("nodac",N)]:
  s=d["co2store"];print(n,"STORE Mt",(s.groupby(["reservoir","year"]).co2.sum()/1e3).round(2).to_dict())
  c=d["co2net"];c=c[c.role=="captured"];print(n,"CAPT Mt",(c.groupby(["source","year"]).co2.sum().unstack().fillna(0)/1e3).round(1).to_string())
  print(n,"EMIS Mt",(d["emis"].groupby("year").co2.sum()/1e3).round(1).to_dict(),"atm",d["atm"].level.round(1).tolist())
  p=d["prod"];print(n,"prod sum",nb(p).groupby("year").output.sum().round(0).to_dict())
  print(n,"CO2 pipe",(d["co2pipe"].groupby("year").co2.sum()/1e3).round(1).to_dict())
