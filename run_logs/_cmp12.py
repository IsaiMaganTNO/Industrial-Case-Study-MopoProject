import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for lbl,d in (("base",a),("new ",b)):
    p=d["prod"]
    tot=p[p["tech"].str.contains(r"\(LN\+EL\)O",na=False,regex=True)]
    print("%s (LN+EL)O output by year: %s"%(lbl,dict(tot.groupby("year")["output"].sum())))
