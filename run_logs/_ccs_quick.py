import pickle
for k in ["nb_v2","nb_ccslow"]:
  d=pickle.load(open(rf"run_logs\{k}.pkl","rb"))
  e=d["emis"]; s=d["co2store"]
  print(k,"net CO2 Mt",(e.groupby("year").co2.sum()/1e3).round(1).to_dict(),"stored Mt",(s.groupby("year").co2.sum()/1e3).round(1).to_dict())
