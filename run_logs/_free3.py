import collections
from spinedb_api import DatabaseMapping
for n in ["nb_v2","mr_fix"]:
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"
  with DatabaseMapping("sqlite:///"+inp) as db:
    cap={}
    for x in db.get_parameter_value_items(entity_class_name="unit__to_node",parameter_definition_name="capacity_per_unit"):
      try: cap[x["entity_byname"][0]]=max(cap.get(x["entity_byname"][0],0),float(x["parsed_value"]))
      except: pass
    cand={x["entity_name"] for x in db.get_parameter_value_items(entity_class_name="unit",parameter_definition_name="investment_count_max_cumulative")}
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    ia={x["entity_byname"][1]:max(float(v) for v in x["parsed_value"].values) for x in db.get_parameter_value_items(parameter_definition_name="units_invested_available")}
    mo=collections.defaultdict(float)
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      u=x["entity_byname"][1]
      if x["entity_byname"][3]=="to_node": mo[u]=max(mo[u],max(float(v) for v in x["parsed_value"].values))
  noncand=[u for u in mo if u not in cand and mo[u]>1e-3]
  free=[u for u in cand if u in cap and mo.get(u,0)>ia.get(u,0)*cap[u]*1.001+1e-3]
  print(n,"candidate units producing above invested capacity:",len(free),collections.Counter(u.rsplit("_",1)[0] for u in free).most_common(15))
  print("  non-candidate producing units:",len(noncand))
