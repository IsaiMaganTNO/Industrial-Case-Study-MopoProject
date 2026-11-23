import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
M=pickle.load(open(r"run_logs\mr_fix.pkl","rb"))
def cty(df):
    r=df.region.astype(str); return r.str.extract(r"^([A-Z]{2})")[0].where(df.region.notna(),"OFF")
e=M["emis"].copy(); e["c"]=cty(e)
o=e.groupby(["c","tech","year"]).co2.sum().unstack().fillna(0)/1e3
print("== negative/large emitters 2050\n",o[(o[2050].abs()>3)].round(1).to_string())
p=M["prod"].copy(); p["c"]=cty(p)
print("== industry: unabated reference share 2050 by country/sector")
for (c,s),g in p.groupby(["c","sector"]):
    q=g.groupby(["tech","year"]).output.sum().unstack().fillna(0)
    if 2050 not in q: continue
    q=(q[2050]/q[2050].sum()*100).round(0); q=q[q>0]
    print(c,s,dict(q))
f=M["fleet"].copy(); f["c"]=cty(f)
for pat,lab in [(r"^wind-off","offshore"),(r"^wind-on","onshore"),(r"^solar","solar"),(r"^nuclear","nuclear"),(r"^PEM","PEM"),(r"^DAC","DAC")]:
    x=f[f.tech.astype(str).str.contains(pat)].groupby(["c","year"]).units.sum().unstack().fillna(0).round(1)
    print("FLEET GW",lab); print(x.to_string())
