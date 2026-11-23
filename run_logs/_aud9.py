import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; e=b["emis"]
for s in ("chlorine","steel (secondary)","cement"):
    print("=== %s ==="%s)
    for y in (2030,2040,2050):
        q=p[(p["year"]==y)&(p["sector"]==s)]
        g=q.groupby("tech")["output"].sum()
        o=g.sum()
        c=e[(e["year"]==y)&(e["tech"].isin(set(g.index)))]["co2"].sum()
        print("  %d out=%8.1f co2=%9.1f int=%.4f  mix=%s"%(y,o,c,c/o if o else 0,
          " ".join("%s=%.0f"%(k[:14],v) for k,v in g.sort_values(ascending=False).items() if v>1)[:46]))
