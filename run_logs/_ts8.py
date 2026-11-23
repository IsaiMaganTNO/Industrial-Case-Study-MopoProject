from spinedb_api import DatabaseMapping,from_database
M=r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite";R=r"sqlite:///checkpoints/Investment_Results.3day_nodac_nuc.sqlite"
ent=None
with DatabaseMapping(M) as m:
  for v in m.get_parameter_value_items(parameter_definition_name="investment_count_fix_cumulative"):
    if v["alternative_name"] in("GA_flex0","GA_flex20"):
      if ent is None: ent=v["entity_byname"]
      if v["entity_byname"]==ent: x=from_database(v["value"],v["type"]);print(ent,v["alternative_name"],getattr(x,"values",x))
  for v in m.get_parameter_value_items(parameter_definition_name="balance_type"): print(v["entity_byname"],v["alternative_name"],from_database(v["value"],v["type"]))
with DatabaseMapping(R) as r:
  for v in r.get_parameter_value_items(parameter_definition_name="units_invested_available"):
    if ent[0] in v["entity_byname"]: print("RESULT",v["entity_byname"],from_database(v["value"],v["type"]).values)
