import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]; e=d["emis"]
al=p[p["sector"]=="aluminium"]
print("aluminium sector output by year x tech:")
print(al.groupby(["year","tech"])["output"].sum().to_string())
print("\naluminium-primary-production-reference emis by year x category:")
t=e[e["tech"]=="aluminium-primary-production-reference"]
print(t.groupby(["year","category"])["co2"].sum().to_string())
