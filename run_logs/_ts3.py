from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for v in m.get_parameter_value_items(entity_class_name="temporal_block",entity_name="planning"): x=from_database(v["value"],v["type"]); print([str(d) for d in x.values])
