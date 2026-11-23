import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
p=d["prod"]
for y in (2030,2050):
    print("=== %d ==="%y)
    q=p[p["year"]==y]
    for sec in sorted(q["sector"].dropna().unique()):
        g=q[q["sector"]==sec].groupby("tech")["output"].sum().sort_values(ascending=False)
        g=g[g>0.5]
        if len(g)==0: continue
        tot=g.sum()
        items=list(g.items())[:4]
        top=", ".join("%s %.0f%%"%(k[:20],100*v/tot) for k,v in items)
        print("  %-17s %8.0f | %s"%(sec[:17],tot,top))
    print()
