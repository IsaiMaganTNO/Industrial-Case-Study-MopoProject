from spinedb_api import DatabaseMapping
with DatabaseMapping("sqlite:///"+r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite") as db:
  for x in db.get_parameter_value_items(entity_class_name="unit__to_node", parameter_definition_name="capacity_per_unit"):
    if x["entity_byname"][0] in ("DAC_NLC1","DAC_UK"): print(x["entity_byname"],x["parsed_value"])
  for d in db.get_parameter_definition_items(entity_class_name="unit"):
    if d["name"] in ("number_of_units","existing_units","investment_count_initial_cumulative","units_existing"): print("default",d["name"],d["parsed_value"] if "parsed_value" in d else d["default_value"])
