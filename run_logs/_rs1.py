from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite") as m:
  for v in m.get_parameter_value_items(entity_name="CO2-storage-NSNL012",parameter_definition_name="storage_investment_count_fix_cumulative"):
    x=from_database(v["value"],v["type"]); print(v["alternative_name"],[str(i)[:10] for i in x.indexes],x.values.round(4))
