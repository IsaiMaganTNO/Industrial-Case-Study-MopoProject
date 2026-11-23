import pickle,pandas as pd
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); s=d["supply"]
    o=s[s["tech"]=="oil-eng"]
    g=o.groupby("year")["energy"].sum()
    fl=d["fleet"]; fo=fl[fl["tech"]=="oil-eng"].groupby("year")["units"].sum()
    print("%s oil-eng energy:"%tag, {int(k):round(v,1) for k,v in g.items()},
          " units:", {int(k):round(v,2) for k,v in fo.items()})
