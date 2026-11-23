import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
fl=b["flows"]
print("flows cols:",list(fl.columns))
h=fl[fl["node"].astype(str).str.startswith("H2")] if "node" in fl.columns else None
print("H2 rows:",len(h) if h is not None else "n/a")
if h is not None: print(h.head(6).to_string())
