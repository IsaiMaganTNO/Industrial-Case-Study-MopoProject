import pickle, pandas as pd
pd.set_option("display.width",250)
M=pickle.load(open(r"run_logs\mixedres.pkl","rb")); V=pickle.load(open(r"run_logs\vre15.pkl","rb"))
def ctry(r): r=str(r); return r[:2] if len(r)>2 and r[2]=="C" else r
for nm,F in [("vre15",V),("mixed",M)]:
    s=F["supply"]; s=s[s.carrier=="electricity"].copy(); s["c"]=s.region.map(ctry)
    g=s[s.tech.str.contains("CCGT|OCGT|gas|nuclear|bio|waste",case=False)]
    print(f"=== {nm}: gas/nuclear/bio electricity by tech x country, 2050 (TWh)")
    print((g[g.year==2050].groupby(["tech","c"]).energy.sum().unstack(fill_value=0)/1e3).round(1).to_string())
print("\n=== methane supply by source tech x country (TWh) mixed")
s=M["supply"]; s=s[s.carrier=="methane"].copy(); s["c"]=s.region.map(ctry)
print((s.groupby(["tech","c","year"]).energy.sum().unstack(fill_value=0)/1e3).round(1).to_string())
print("\n=== methane supply vre15 (TWh)")
s=V["supply"]; s=s[s.carrier=="methane"].copy(); s["c"]=s.region.map(ctry)
print((s.groupby(["tech","c","year"]).energy.sum().unstack(fill_value=0)/1e3).round(1).to_string())
