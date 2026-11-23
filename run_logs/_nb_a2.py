import pickle,re,pandas as pd
from spinedb_api import DatabaseMapping,from_database
B=pickle.load(open(r"run_logs\nb_v2.pkl","rb"))
c=B["co2net"];print("DAC rows",c[c.source=="direct air capture"].groupby(["tech","region","year"]).co2.sum().round(1).to_dict())
f=B["fleet"];print("DAC fleet",f[f.tech.astype(str).str.contains("DAC")].groupby(["tech","region","year"]).units.sum().to_dict())
R=r"sqlite:///checkpoints/Investment_Results.3day_nb_v2.sqlite"
use={}
with DatabaseMapping(R) as m:
  for v in m.get_parameter_value_items(parameter_definition_name="node_state_longterm"):
    e=v["entity_byname"]
    if any(x.startswith("biomass-stock_") for x in e):
      x=from_database(v["value"],v["type"]); use[[x for x in e if x.startswith("biomass-stock_")][0]]=[(str(i)[:10],round(float(y),2)) for i,y in zip(x.indexes,x.values)]
for k in sorted(use)[:4]: print(k,use[k])
M=r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
cap={}
with DatabaseMapping(M) as m:
  for v in m.get_parameter_value_items(parameter_definition_name="storage_investment_count_initial_cumulative",alternative_name="medium_bio"):
    cap[v["entity_byname"][0]]=float(from_database(v["value"],v["type"]))
print("endowment sum (x365 TWh)",round(sum(cap.values())*365))
