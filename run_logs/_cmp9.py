import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for lbl,d in (("base",a),("new ",b)):
    s=d["co2store"]; q=s[s["year"]==2050]
    g=q.groupby("reservoir")["co2"].max()
    print("%s 2050 peak level per reservoir:"%lbl)
    for k,v in g.items(): print("    %-24s %10.3f"%(k,v))
print()
for lbl,d in (("base",a),("new ",b)):
    e=d["emis"]; q=e[(e["year"]==2050)&(e["tech"].str.contains("DAC",na=False))]
    print("%s 2050 DAC co2 = %.1f"%(lbl,q["co2"].sum()))
