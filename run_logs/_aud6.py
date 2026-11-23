import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
e=b["emis"]
q=e[e["year"]==2050].groupby(["category","tech"])["co2"].sum()
q=q[q.abs()>1].sort_values(key=abs,ascending=False)
print("2050 ALL techs with |co2|>1:")
for (cat,t),v in q.items(): print("  %-26s %-30s %12.1f"%(cat[:26],str(t)[:30],v))
