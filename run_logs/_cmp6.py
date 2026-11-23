import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for y in (2030,2040,2050):
    ea=a["emis"]; eb=b["emis"]
    ga=ea[ea["year"]==y].groupby("category")["co2"].sum()
    gb=eb[eb["year"]==y].groupby("category")["co2"].sum()
    ks=sorted(set(ga.index)|set(gb.index))
    print("=== %d ==="%y)
    for k in ks:
        x=ga.get(k,0.0); z=gb.get(k,0.0)
        if abs(x)<1 and abs(z)<1: continue
        print("  %-34s %12.1f -> %12.1f  (%+.1f)"%(k[:34],x,z,z-x))
    print("  %-34s %12.1f -> %12.1f  (%+.1f)"%("TOTAL",ga.sum(),gb.sum(),gb.sum()-ga.sum()))
