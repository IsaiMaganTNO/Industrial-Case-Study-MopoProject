import pickle
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
e=d["emis"]
q=e[e["year"]==2050]
g=q.groupby("tech")["co2"].sum().sort_values()
print("2050 all nonzero emitters:")
for k,v in g.items():
    if abs(v)<1: continue
    print("   %-28s %12.1f"%(k[:28],v))
print("\nnet %.1f"%g.sum())
