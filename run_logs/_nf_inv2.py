import pickle,pandas as pd,sys
sys.path.insert(0,"tools");import postprocess as PP
pd.set_option("display.width",250)
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
s=B["supply"];s=s[(s.carrier=="electricity")&(s.energy>0)]
s=s.assign(reg=s.region.fillna("offshore"))
print("== elec by category TWh (incl offshore nodes)");print((s.groupby(["category","year"]).energy.sum().unstack().fillna(0)/1e3).round(1).to_string())
f=B["fleet"];v=f[f.category.astype(str).str.contains("wind|solar",case=False)]
print("== VRE fleet GW");print(v.groupby(["category","year"]).units.sum().unstack().round(1).to_string())
print(v[v.category.astype(str).str.contains("offshore")].groupby(["tech","year"]).units.sum().unstack().round(2).to_string())
c=nb(B["co2net"]);c=c[c.role=="captured"];print("== captured by source Mt");print((c.groupby(["source","year"]).co2.sum().unstack().fillna(0)/1e3).round(2).to_string())
print("== pipes");print((B["co2pipe"].groupby(["connection","year"]).co2.sum().unstack().fillna(0)/1e3).round(2).to_string())
print("obj",B["obj"].round(0).to_dict())
