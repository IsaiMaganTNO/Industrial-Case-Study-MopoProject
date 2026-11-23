import pickle,pandas as pd
pd.set_option("display.width",250)
N=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
e=N["emis"]; o=e[e.category=="other"].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3
print(o[(o.abs()>.2).any(axis=1)].round(2).to_string())
print("ALL regions emis",(e.groupby("year").co2.sum()/1e3).round(2).to_dict())
i=e[e.category.str.startswith("industry")].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3
print(i[(i.abs()>.2).any(axis=1)].round(2).to_string())
p=nb(N["prod"]);print("prod dup rows",len(p),len(p.drop_duplicates()))
print((p.groupby(["sector","year"]).output.sum().unstack()).round(0).to_string())
c=N["co2net"];print((c.groupby(["role","year"]).co2.sum().unstack()/1e3).round(2).to_string())
