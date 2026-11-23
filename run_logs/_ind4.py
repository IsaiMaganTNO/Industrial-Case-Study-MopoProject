import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
e=d["emis"]; p=d["prod"]
q=e[(e["year"]==2050)]
g=q.groupby("tech")["co2"].sum()
pr=p[p["year"]==2050].groupby("tech")["output"].sum()
print("%-28s %12s %12s"%("tech (2050, producing)","output","co2"))
for k,v in pr.sort_values(ascending=False).items():
    if v<1: continue
    print("%-28s %12.0f %12.1f"%(k[:28],v,g.get(k,float('nan'))))
