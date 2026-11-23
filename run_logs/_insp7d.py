import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
for k in ("supply","fleet"):
    f=d[k]; print("==",k,list(f.columns))
    print(f.head(4).to_string()[:400]); print()
