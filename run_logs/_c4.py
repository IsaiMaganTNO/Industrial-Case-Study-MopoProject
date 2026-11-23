import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]
q=p[(p["sector"]=="cement")&(p["year"]==2050)]
print("2050 cement output by region x tech:")
print(q.groupby(["region","tech"])["output"].sum().to_string())
