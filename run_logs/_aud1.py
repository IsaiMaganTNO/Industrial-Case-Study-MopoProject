import pickle,re
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; e=b["emis"]
# every tech that PRODUCES in 2050 but books ZERO co2
q=p[p["year"]==2050].groupby("tech")["output"].sum()
em=e[e["year"]==2050].groupby("tech")["co2"].sum()
print("%-40s %10s %10s"%("tech producing 2050 with ZERO co2","output","co2"))
n=0
for t,o in q.sort_values(ascending=False).items():
    if o<1: continue
    c=em.get(t,0.0)
    if abs(c)<1e-6:
        print("%-40s %10.1f %10.3f"%(str(t)[:40],o,c)); n+=1
print("count:",n)
