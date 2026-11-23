import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
ea=a["emis"];eb=b["emis"]
for y in (2050,):
    qa=ea[(ea["year"]==y)&(ea["category"]=="other")].groupby("tech")["co2"].sum()
    qb=eb[(eb["year"]==y)&(eb["category"]=="other")].groupby("tech")["co2"].sum()
    ks=sorted(set(qa.index)|set(qb.index),key=lambda k:-abs(qb.get(k,0)-qa.get(k,0)))
    print("=== %d 'other' biggest movers ==="%y)
    for k in ks[:10]:
        x=qa.get(k,0.0);z=qb.get(k,0.0)
        print("  %-36s %11.1f -> %11.1f (%+.1f)"%(k[:36],x,z,z-x))
