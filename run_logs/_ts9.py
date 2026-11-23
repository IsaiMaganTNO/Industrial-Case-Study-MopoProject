from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for a in m.get_alternative_items(): print(a["id"],a["name"],end=" | ")
  print()
  for v in m.get_parameter_value_items(entity_name="fossil-CH4"): print(v["parameter_definition_name"],v["alternative_name"],from_database(v["value"],v["type"]))
with DatabaseMapping(r"sqlite:///checkpoints/Investment_Results.3day_nodac_nuc.sqlite") as r:
  for v in r.get_parameter_value_items():
    if "fossil-CH4" in v["entity_byname"]:
      x=from_database(v["value"],v["type"]); print(v["entity_byname"],v["parameter_definition_name"],[round(float(y),2) for y in x.values][:6])
