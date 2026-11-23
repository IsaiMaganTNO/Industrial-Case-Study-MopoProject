import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
p=d["prod"]
for y in (2030,2050):
    print("=== %d production by sector/tech (top routes) ==="%y)
    q=p[p["year"]==y]
    for sec in sorted(q["sector"].dropna().unique()):
        s=q[q["sector"]==sec]
        g=s.groupby("tech")["output"].sum().sort_values(ascending=False)
        g=g[g>0.5]
        if g.empty: continue
        tot=g.sum()
        top=", ".join("%s %.0f%%"%(k[:22],100*v/tot) for k,v in g.items()[:4]) if hasattr(g,'items') else ""
        print("  %-18s tot=%8.0f | %s"%(sec[:18],tot,top))
    print()
