import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",200)
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
p=nb(B["prod"])
print("== route shares %")
for s,g in p.groupby("sector"):
  q=g.groupby(["tech","year"]).output.sum().unstack().fillna(0);q=(q/q.sum()*100).round(0);print("--",s);print(q[(q>0).any(axis=1)].to_string())
e=nb(B["emis"]);x=e.groupby(["category","year"]).co2.sum().unstack().fillna(0)/1e3;print("== emis cat\n",x.round(2).to_string())
o=e[e.co2.abs()>0].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3;print("== emis tech >0.3\n",o[(o.abs()>.3).any(axis=1)].round(2).to_string())
c=B["co2net"];print("== co2 roles\n",(c.groupby(["role","year"]).co2.sum().unstack()/1e3).round(2).to_string())
f=nb(B["fleet"]);v=f[f.category.astype(str).str.contains("wind|solar",case=False)].groupby(["category","year"]).units.sum().unstack().round(1);print("== VRE GW\n",v.to_string())
k=f.groupby(["tech","year"]).units.sum().unstack().fillna(0);print("== fleet GW top\n",k[k.max(axis=1)>1].round(1).to_string())
print("atm",B["atm"].to_string())
