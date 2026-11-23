import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; f=b["fleet"]
print("REF-SMR vs REF-SMR-MEA: fleet UNITS and actual OUTPUT 2050")
for t in ("REF-SMR","REF-SMR-MEA"):
    u=f[(f["tech"]==t)&(f["year"]==2050)]["units"].sum()
    o=p[(p["tech"]==t)&(p["year"]==2050)]["output"].sum()
    print("   %-14s units=%8.2f  output=%10.1f"%(t,u,o))
print("\n=> 80.39 units of unabated REF-SMR remain in the FLEET in 2050.")
