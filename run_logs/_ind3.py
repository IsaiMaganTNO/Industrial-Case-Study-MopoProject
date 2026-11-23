import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
e=d["emis"]
print("categories:",sorted(e["category"].dropna().unique()))
for y in (2030,2050):
    q=e[e["year"]==y]
    g=q.groupby("category")["co2"].sum().sort_values()
    print("=== %d ==="%y)
    for k,v in g.items(): print("   %-22s %12.1f"%(k[:22],v))
