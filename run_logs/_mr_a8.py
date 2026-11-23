import pickle
m=pickle.load(open(r"run_logs\mixedres.pkl","rb"));v=pickle.load(open(r"run_logs\vre15.pkl","rb"))
for n,d in [("mix",m),("v15",v)]:
  e=d["co2net"];print(n,"net by year",e.groupby("year").co2.sum().round(1).to_dict())
  print(e[e.tech.astype(str).str.contains("DAC")].groupby(["region","year"]).co2.sum().round(1).to_dict())
  i=d["inv"];print("DAC inv",i[i.tech=="DAC"].groupby("region").units.sum().round(2).to_dict())
