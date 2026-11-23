from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for s in m.get_scenario_alternative_items(): print(s["scenario_name"],s["rank"],s["alternative_name"])
  for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
    if v["entity_byname"][0].startswith("invest") or v["entity_byname"][0]=="planning": print(v["entity_byname"],v["parameter_definition_name"],from_database(v["value"],v["type"]))
  for v in m.get_parameter_value_items(entity_class_name="model"): print(v["entity_byname"],v["parameter_definition_name"],from_database(v["value"],v["type"]))
