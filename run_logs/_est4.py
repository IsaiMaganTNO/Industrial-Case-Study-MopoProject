import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]; e=d["emis"]
s=p[p["tech"]=="aluminium-primary-production-reference"]
print("prod aluminium by year:"); print(s.groupby("year")["output"].agg(["count","sum"]))
print("\nprod aluminium dtypes year:",p["year"].dtype)
t=e[e["tech"]=="aluminium-primary-production-reference"]
print("\nemis aluminium by year:"); print(t.groupby("year")["co2"].agg(["count","sum"]))
print("\nall prod years counts:"); print(p.groupby("year")["output"].agg(["count","sum"]))
