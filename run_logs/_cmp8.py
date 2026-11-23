import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for lbl,d in (("base",a),("new ",b)):
    s=d["co2store"]
    print("=== %s co2store 2050 ==="%lbl)
    q=s[s["year"]==2050] if "year" in s.columns else s
    print(q.to_string()[:700])
