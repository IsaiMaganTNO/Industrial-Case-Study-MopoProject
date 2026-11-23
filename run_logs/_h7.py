import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
s=b["supply"]
h=s[s["carrier"]=="hydrogen"]
print("hydrogen rows:",len(h))
for y in (2030,2040,2050):
    q=h[h["year"]==y]
    print("--- %d  TOTAL=%.0f GWh ---"%(y,q["energy"].sum()))
    for t,v in q.groupby("tech")["energy"].sum().sort_values(ascending=False).items():
        if abs(v)>1: print("    %-26s %12.0f"%(str(t)[:26],v))
