import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
for lbl,d in (("base",a),("new ",b)):
    e=d["emis"]; q=e[e["year"]==2050]
    neg=q[q["co2"]<0].groupby("tech")["co2"].sum().sort_values()
    print("%s 2050 NEGATIVE-emission techs:"%lbl)
    for k,v in neg.items():
        if v<-1: print("    %-36s %12.1f"%(k[:36],v))
