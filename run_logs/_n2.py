import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
f=b["fleet"]; p=b["prod"]; s=b["supply"]
for t in ("nuclear-3","nuclear-3-existing"):
    q=f[f["tech"]==t]
    print("fleet %-20s %s"%(t,{y:round(q[q["year"]==y]["units"].sum(),3) for y in (2030,2040,2050)} if len(q) else "ABSENT"))
el=s[s["carrier"]=="electricity"]
print("\n2050 electricity supply by tech (top 14):")
q=el[el["year"]==2050].groupby("tech")["energy"].sum().sort_values(ascending=False)
tot=q.sum()
for t,v in q.head(14).items():
    if v>1: print("   %-22s %10.0f  %5.2f%%"%(str(t)[:22],v,100*v/tot))
print("   TOTAL %.0f GWh"%tot)
