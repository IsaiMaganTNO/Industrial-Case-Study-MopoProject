import pickle,pandas as pd
for nm,p in [("MR",r"run_logs\mr_fix_NLBE.pkl"),("NB",r"run_logs\nb_v2.pkl")]:
    d=pickle.load(open(p,"rb")); f=d["fleet"]
    if nm=="NB": f=f[f.region.isna()|f.region.astype(str).str.match(r"^(BE|NL)C\d")]
    print("==",nm)
    for pat,l in [(r"^wind-off","off"),(r"^wind-on","on"),(r"^solar","pv"),(r"^nuclear","nuc"),(r"^PEM","PEM"),(r"^REF-SMR","SMR"),(r"^gas-boiler","gasboil"),(r"^battery","batt")]:
        print(l,f[f.tech.astype(str).str.contains(pat)].groupby("year").units.sum().round(1).to_dict())
    s=d["supply"]; s=s[(s.energy>0)]
    if nm=="NB": s=s[s.region.isna()|s.region.astype(str).str.match(r"^(BE|NL)C\d")]
    print("elec TWh",(s[s.carrier=="electricity"].groupby("year").energy.sum()/1e3).round(0).to_dict())
    print("H2 TWh",(s[s.carrier=="hydrogen"].groupby(["tech","year"]).energy.sum().unstack().fillna(0)/1e3).round(0).query("`2050`>2").to_dict("index"))
