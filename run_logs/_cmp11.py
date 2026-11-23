import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
print("=== P6/P7 olefins mix ===")
for y in (2030,2040,2050):
    print("--- %d ---"%y)
    for lbl,d in (("base",a),("new ",b)):
        p=d["prod"]; q=p[(p["year"]==y)&(p["sector"]=="olefins")]
        g=q.groupby("tech")["output"].sum().sort_values(ascending=False)
        print("   %s %s"%(lbl," ".join("%s=%.0f"%(k[:18],v) for k,v in g.items() if v>1)[:80]))
