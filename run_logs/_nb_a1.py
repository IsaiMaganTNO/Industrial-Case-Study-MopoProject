import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
B=pickle.load(open(r"run_logs\nb_v2.pkl","rb")); O=pickle.load(open(r"run_logs\nn_fix.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
nbo=lambda df:df[df.region.isna()|df.region.astype(str).str.match(NB)]
p=nb(B["prod"])
print("== OUTPUT per sector (must be constant)",p.groupby(["sector","year"]).output.sum().unstack().round(0).to_dict("index"))
print("== route shares %")
for s,g in p.groupby("sector"):
  q=g.groupby(["tech","year"]).output.sum().unstack().fillna(0);q=(q/q.sum()*100).round(0);print("--",s);print(q[(q>0).any(axis=1)].to_string())
e=nb(B["emis"])
print("== emis by category Mt\n",(e.groupby(["category","year"]).co2.sum().unstack().fillna(0)/1e3).round(2).to_string())
o=e.groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3;print("== emis by tech |>0.3|\n",o[(o.abs()>.3).any(axis=1)].round(2).to_string())
print("== emis total all",(B["emis"].groupby("year").co2.sum()/1e3).round(2).to_dict())
c=B["co2net"];print("== co2 roles\n",(c.groupby(["role","year"]).co2.sum().unstack()/1e3).round(2).to_string())
print("== captured by source\n",(c[c.role=="captured"].groupby(["source","year"]).co2.sum().unstack().fillna(0)/1e3).round(1).to_string())
s=B["co2store"];print("== storage",(s.groupby(["reservoir","year"]).co2.sum()/1e3).round(2).to_dict())
S=nbo(B["supply"]);S=S[S.energy>0]
for car in ["electricity","methane","hydrogen","heat"]:
  x=S[S.carrier==car].groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3
  print("==",car,"TWh total",x.sum().round(1).to_dict());print(x[(x>2).any(axis=1)].round(1).to_string())
f=nbo(B["fleet"])
for pat,lab in [(r"^wind-off","offshore"),(r"^wind-on","onshore"),(r"^solar","solar"),(r"^nuclear-3$","nuclear new"),(r"^PEM","PEM"),(r"^REF-SMR","SMR"),(r"^gas-boiler","gas boiler"),(r"heatpump","heat pumps"),(r"^battery","battery"),(r"^DAC","DAC"),(r"^harber","Haber-Bosch")]:
  x=f[f.tech.astype(str).str.contains(pat)].groupby("year").units.sum().round(2).to_dict();print("FLEET",lab,x)
x=f[f.tech=="nuclear-3"];print("nuclear by country",x.assign(c=x.region.astype(str).str[:2]).groupby(["c","year"]).units.sum().round(2).to_dict())
