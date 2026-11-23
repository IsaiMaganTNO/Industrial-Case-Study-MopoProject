import pickle
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb"))
    o=d["obj"]
    print(tag,"objective:",{k:round(float(v),1) for k,v in list(o.items())[:6]})
