import pickle,re,pandas as pd
from spinedb_api import DatabaseMapping
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  U=pd.Series(d["U"]).rename("v").reset_index(); U.columns=["y","c","car","dr","fam","v"]; U=U[U.y==2050]
  b=U[U.car.isin(["bio","biomass-stock"])&U.c.isin(["NL","BE"])]
  print(k,"bio flows TWh:",(b.groupby(["car","dr","fam"]).v.sum()/1e3).round(1)[lambda s:s.abs()>0.3].to_dict())
  lh=U[U.fam=="LH2-terminal"]; print("  LH2 by country:",(lh[lh.car=="H2"].groupby("c").v.sum()/1e3).round(1).to_dict())
for n in ["nb_ccslow","mr_ccslow_dac0"]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite") as db:
    s={}
    for v in db.get_parameter_value_items(entity_class_name="node"):
      if v["entity_name"].startswith("biomass-stock") and v["parameter_definition_name"] in ("initial_node_state","storages_existing","node_state_cap","storage_capacity"):
        pv=v["parsed_value"]; s.setdefault(v["parameter_definition_name"],{})[v["entity_name"]+"|"+v["alternative_name"]]=pv if isinstance(pv,float) else str(pv)[:60]
    for kk,vv in s.items(): print(n,kk,list(vv.items())[:6], "n=",len(vv))
