import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
f=b["fleet"]; d=b["decom"]
print("=== REF-SMR family: existing unabated vs new MEA ===")
for t in ("REF-SMR","REF-SMR-MEA"):
    q=f[f["tech"]==t]
    print("  fleet %-12s %s"%(t,{y:round(q[q["year"]==y]["units"].sum(),2) for y in (2030,2040,2050)}))
print("\n=== decom frame: is existing capacity retired when MEA appears? ===")
for t in ("REF-SMR","CCGT-existing","BF-BOF"):
    q=d[d["tech"]==t]
    if len(q): print("  decom %-14s %s"%(t,{y:round(q[q["year"]==y]["units"].sum(),2) for y in (2030,2040,2050)}))
    else: print("  decom %-14s none"%t)
