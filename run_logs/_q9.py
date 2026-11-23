import pickle,re,pandas as pd
from spinedb_api import DatabaseMapping
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  C=pd.Series(d["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]; C=C[(C.y==2050)&(C.dr=="to_node")]
  b=C[C.node.str.startswith("bio_")]; b=b.assign(c=b.node.str[4:6], src=b.cn.str.replace(r"_.*","",regex=True))
  print(k,"into bio_ nodes TWh:",(b.groupby(["c","src"]).v.sum()/1e3).round(1)[lambda s:s>0.2].to_dict())
with DatabaseMapping("sqlite:///"+r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite") as db:
  ps={}
  for v in db.get_parameter_value_items(entity_class_name="node"):
    if v["entity_name"].startswith("biomass-stock_NLC1"): print(v["parameter_definition_name"],v["alternative_name"],str(v["parsed_value"])[:120])
  print([c["entity_byname"] for c in db.get_entity_items(entity_class_name="connection__from_node") if "biomass-stock_NLC1" in c["entity_byname"]][:3])
