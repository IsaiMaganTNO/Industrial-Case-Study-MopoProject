import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
for k in ("prod","emis","fleet"):
    f=d[k]; print(k,"cols:",list(f.columns)); print("  years:",sorted(set(f["year"])))
p=d["prod"]
s=p[p["tech"]=="aluminium-primary-production-reference"]
print("\nrows for aluminium in prod:",len(s))
print(s.head(12).to_string())
