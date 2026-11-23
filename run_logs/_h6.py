import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
s=b["supply"]
print("carriers:",sorted(set(str(x) for x in s["carrier"])))
h=s[s["carrier"].astype(str).str.upper()=="H2"]
print("H2 rows:",len(h))
for y in (2030,2040,2050):
    q=h[h["year"]==y]
    print("--- %d  total=%.0f GWh ---"%(y,q["energy"].sum()))
    for t,v in q.groupby("tech")["energy"].sum().sort_values(ascending=False).items():
        if abs(v)>1: print("    %-24s %12.0f"%(str(t)[:24],v))
