from spinedb_api import DatabaseMapping
for n in ["nb_v2","mr_fix"]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite") as db:
    for x in db.get_parameter_value_items(entity_class_name="unit"):
      if x["entity_name"] in ("DAC_NLC1","DAC_UK"): print(n,x["entity_name"],x["parameter_definition_name"],x["alternative_name"],str(x["parsed_value"])[:60])
