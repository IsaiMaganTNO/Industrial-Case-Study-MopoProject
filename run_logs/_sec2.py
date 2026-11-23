import pickle
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
p=d["prod"]
for s in ["chlorine","steel (secondary)","aluminium","cement"]:
    print("==",s)
    for y in (2030,2040,2050):
        q=p[(p["sector"]==s)&(p["year"]==y)]
        g=q.groupby("tech")["output"].sum()
        g=g[g>0.1]
        print("   %d: %s"%(y,{k[:26]:round(v,0) for k,v in g.items()}))
