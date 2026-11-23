import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
e=d["emis"]; print("emis cols:",list(e.columns))
y=e[e["year"]==2050]
col=[c for c in e.columns if e[c].dtype.kind in "fi" and c!="year"]
print("2050 pos=%.1f neg=%.1f net=%.1f"%(
  y[y[col[0]]>0][col[0]].sum(), y[y[col[0]]<0][col[0]].sum(), y[col[0]].sum()))
t=y.groupby("tech")[col[0]].sum().sort_values()
print("\nmost negative:"); print(t.head(6).to_string())
print("\nmost positive:"); print(t.tail(6).to_string())
