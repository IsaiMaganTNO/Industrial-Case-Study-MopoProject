import pickle,re,pandas as pd
from spinedb_api import DatabaseMapping
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  C=pd.Series(d["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]; C=C[(C.y==2050)&(C.dr=="to_node")]
  e=C[C.cn.str.contains("_elec_")]; e=e[e.cn.str.match(r"^(DE|FR|LU|UK|DK|NO|NLC\d|BEC\d|NL|BE)_elec_")]
  e=e.assign(o=e.cn.str.split("_").str[0].str[:2], dest=e.node.str.split("_").str[-1].str[:2])
  x=e[e.o!=e.dest].groupby(["o","dest"]).v.sum()/1e3
  print(k,"elec cross-border TWh 2050:",x[x>0.1].round(1).to_dict())
  U=pd.Series(d["U"]).rename("v").reset_index(); U.columns=["y","c","car","dr","fam","v"]
  b=U[(U.y==2050)&(U.fam.str.startswith("biomass"))]; print("  biomass supply units:",(b.groupby(["c","fam","car","dr"]).v.sum()/1e3).round(1).to_dict())
p=r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite"
with DatabaseMapping("sqlite:///"+p) as db:
  for v in db.get_parameter_value_items(entity_class_name="node"):
    if re.match(r"^(bio|biomass)",v["entity_name"]) and v["parameter_definition_name"] in("node_state_cap","initial_node_state","storage_state_max","node_state_min","fix_node_state"): print(v["entity_name"],v["parameter_definition_name"],v["alternative_name"],str(v["parsed_value"])[:80])
  print([e["name"] for e in db.get_entity_items(entity_class_name="unit") if "pulp-production-alternative" in e["name"]][:2])
