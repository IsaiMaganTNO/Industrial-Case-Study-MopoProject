import pickle,pandas as pd
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
s=B["supply"];el=s[s.carrier=="electricity"]
o=el[el.tech.astype(str).str.contains("off")];print("offshore TWh",(o.groupby("year").energy.sum()/1e3).round(1).to_dict(),"regions",o.region.astype(str).unique()[:5])
print("ALL elec TWh by year",(el[el.energy>0].groupby("year").energy.sum()/1e3).round(1).to_dict())
f=B["fleet"];print(f[f.tech.astype(str).str.startswith("REF-SMR")].groupby(["tech","region","year"]).units.sum().round(1).to_string())
c=B["co2net"];print((c[c.role=="captured"].groupby(["source","year"]).co2.sum().unstack().fillna(0)/1e3).round(1).to_string())
