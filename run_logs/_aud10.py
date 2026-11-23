import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; e=b["emis"]
for y in (2040,2050):
    print("=== cement %d per-route ==="%y)
    q=p[(p["year"]==y)&(p["sector"]=="cement")]
    for t,o in q.groupby("tech")["output"].sum().sort_values(ascending=False).items():
        if o<1: continue
        c=e[(e["year"]==y)&(e["tech"]==t)]["co2"].sum()
        print("   %-20s out=%7.0f co2=%8.1f int=%.4f"%(str(t)[:20],o,c,c/o))
