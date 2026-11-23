import pickle,pandas as pd
pd.set_option("display.width",250);pd.set_option("display.max_rows",300)
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
e=nb(B["emis"]); p=nb(B["prod"])
# emissions per industrial sector via tech->sector map from prod
t2s=p.drop_duplicates(["tech"]).set_index("tech").sector
e2=e.assign(sector=e.tech.map(t2s))
x=e2[e2.sector.notna()].groupby(["sector","year"]).co2.sum().unstack().fillna(0)/1e3
print("== EMIS by heavy sector (Mt)");print(x.round(2).to_string())
o=e2[e2.sector.isna()].groupby(["category","year"]).co2.sum().unstack().fillna(0)/1e3;print("== other emis by category");print(o.round(2).to_string())
oi=e2[e2.sector.isna()&e2.category.str.startswith("industry")].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3;print(oi[(oi.abs()>.05).any(axis=1)].round(2).to_string())
oo=e2[e2.sector.isna()&~e2.category.str.startswith("industry")].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3;print(oo[(oo.abs()>.3).any(axis=1)].round(2).to_string())
print("== routes per sector (%)")
for s,g in p.groupby("sector"):
  q=g.groupby(["tech","year"]).output.sum().unstack().fillna(0);q=(q/q.sum()*100).round(0);print("--",s);print(q[(q>0).any(axis=1)].to_string())
print("== fuel use by sector");print(p.groupby(["sector","fuel","year"]).output.sum().unstack().fillna(0).round(0).to_string())
