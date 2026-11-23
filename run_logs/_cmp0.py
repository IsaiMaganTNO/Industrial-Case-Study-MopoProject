import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))      # baseline 3-day
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))  # new
print("obj base:",a.get("obj")); print("obj new :",b.get("obj"))
for k in ("emis","prod","co2net","co2store","atm"):
    print(k,"base rows",len(a[k]) if k in a else "-","new rows",len(b[k]) if k in b else "-")
