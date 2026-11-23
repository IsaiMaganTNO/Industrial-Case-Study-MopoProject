import sys, collections, pickle; sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
n="mr_fix"; inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"
w=PP.load_weights(inp)
with DatabaseMapping("sqlite:///"+inp) as db:
  cand={x["entity_name"] for x in db.get_parameter_value_items(entity_class_name="unit",parameter_definition_name="investment_count_max_cumulative")}
  mx={x["entity_name"]:x["parsed_value"] for x in db.get_parameter_value_items(entity_class_name="unit",parameter_definition_name="investment_count_max_cumulative")}
inv=collections.defaultdict(float)
with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
  names=collections.Counter(x["parameter_definition_name"] for x in db.get_parameter_value_items() if x["entity_class_name"].startswith("report__unit") and x["entity_class_name"].count("__")<=2)
  print("unit-level outputs:",names)
  out=collections.defaultdict(float)
  for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
    u=x["entity_byname"][1]
    if x["entity_byname"][3]=="to_node" and u in cand:
      for y,v in PP.unpack_flow(x,w):
        if int(y)==2050: out[u]+=v
zero=[u for u in cand if mx.get(u)==0 and out.get(u,0)>1]
print("candidate units with max_cumulative=0 but 2050 output>0:",len(zero))
print(collections.Counter(u.rsplit("_",1)[0] for u in zero).most_common(20))
