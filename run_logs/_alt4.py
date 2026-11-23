import pickle
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]
a=p[p["tech"].astype(str).str.contains("alternative")]
g=a[a["year"]==2050].groupby("tech")["output"].sum().sort_values(ascending=False)
print("2050 output on ALTERNATIVE routes (all unbooked):")
print(g[g>0].to_string())
tot=p[p["year"]==2050]["output"].sum()
print("\nalternative share of 2050 industry output: %.1f%%"%(100*g.sum()/tot))
