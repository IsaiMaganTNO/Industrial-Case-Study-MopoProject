import pickle
d=pickle.load(open(r"run_logs\mixedres.pkl","rb"));s=d["co2store"]
print((s.groupby(["reservoir","year"]).co2.sum()/365).round(1).to_string())
