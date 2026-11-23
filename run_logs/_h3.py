import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
f=b["fleet"]; p=b["prod"]
print("FLEET (units) for H2 producers:")
for t in ("PEM","SMR","SMR+CC","REF-SMR","REF-SMR-MEA","LH2-terminal"):
    q=f[f["tech"]==t]
    if len(q): print("  %-14s %s"%(t,{y:round(q[q["year"]==y]["units"].sum(),3) for y in (2030,2040,2050)}))
    else: print("  %-14s ABSENT from fleet"%t)
print("\nflows frame keys:",[k for k in b.keys()])
