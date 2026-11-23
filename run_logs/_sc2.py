import pickle,pandas as pd
pd.set_option("display.width",250)
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
s=nb(B["supply"])
for t in ["REF-SMR-MEA","REF-SMR","gas-boiler","PEM","CCGT-H2","LNG-terminal"]:
  x=s[s.tech==t].groupby(["carrier","year"]).energy.sum().unstack().fillna(0)/1e3;print("==",t);print(x.round(1).to_string())
i=B["inv"];print("== offshore inv",i[i.tech.astype(str).str.contains("off",case=False)].groupby(["tech","year"]).units.sum().round(2).to_dict())
f=B["fleet"];print("== offshore fleet",f[f.tech.astype(str).str.contains("off",case=False)].groupby(["tech","year"]).units.sum().round(2).to_dict())
e=B["emis"];print("== electrolysis emis techs",e[e.category=="electrolysis"].groupby("tech").co2.sum().round(1).to_dict())
h=s[s.carrier.astype(str).str.contains("heat",case=False)].groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3;print("== heat\n",h[(h>3).any(axis=1)].round(1).to_string())
print("carriers",sorted(s.carrier.astype(str).unique()))
