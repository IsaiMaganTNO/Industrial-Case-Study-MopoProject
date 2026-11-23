import pickle
for n in ["mixedres","vre15"]:
  d=pickle.load(open(rf"run_logs\{n}.pkl","rb"));s=d["co2store"];t=s[s.year==2050].groupby("reservoir").co2.sum()/1e3
  print(n,t.round(1).to_dict())
