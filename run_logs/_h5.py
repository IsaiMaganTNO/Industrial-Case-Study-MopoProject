import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for k,v in b.items():
    try: print("%-10s %s"%(k,list(v.columns)))
    except Exception: print("%-10s %s"%(k,type(v).__name__))
