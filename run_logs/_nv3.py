import pickle,pandas as pd
pd.set_option("display.width",250)
N=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"))
p=N["prod"];p=p[p.region.astype(str).str.match(r"^(BE|NL)C\d")]
for s in ["ammonia","olefins","steel (primary)","cement","paper","chlorine"]:
  x=p[p.sector==s].groupby(["tech","year"]).output.sum().unstack().fillna(0)
  print("==",s);print((x/x.sum()*100).round(0).to_string())
S=N["supply"];S=S[S.region.astype(str).str.match(r"^(BE|NL)C\d")&(S.energy>0)]
for car in ["hydrogen","methane"]:
  x=S[S.carrier==car].groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3;print("==",car);print(x[(x>1).any(axis=1)].round(1).to_string())
