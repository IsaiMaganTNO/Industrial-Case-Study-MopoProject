import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
s=d["supply"]
e=s[s["carrier"]=="electricity"]
for y in (2030,2040,2050):
    g=e[e["year"]==y].groupby("tech")["energy"].sum().sort_values(ascending=False)
    tot=g.sum()
    print("=== %d  total %.0f GWh ==="%(y,tot))
    for k,v in g.items():
        if v<1: continue
        print("  %-28s %10.0f  %5.2f%%"%(k[:28],v,100*v/tot))
    print()
