import pickle
d=pickle.load(open(r"run_logs\mixedres.pkl","rb"));s=d["co2store"]
a=s.groupby(["reservoir","year"]).co2.sum()/365
for site,cap in [("CO2-storage-ATUK031",10000),("CO2-storage-NSNL012",21000)]:
  print(site,{y:round(a.get((site,y),0),1) for y in (2030,2040,2050)},"cap",cap)
