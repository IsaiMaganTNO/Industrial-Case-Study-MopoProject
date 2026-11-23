import sqlite3,sys
from spinedb_api import DatabaseMapping,from_database
db=r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite"
with DatabaseMapping(db) as m:
  for v in m.get_parameter_value_items():
    ent="__".join(v["entity_byname"]); p=v["parameter_definition_name"]
    if (p in("storage_investment_count_fix_cumulative","storage_investment_count_max_cumulative") and "NSNL" in ent) or (p in("block_start","block_end","resolution") ) or (ent=="atmosphere" or "atmos" in ent and "state" in p):
      x=from_database(v["value"],v["type"]); print(ent,p,v["alternative_name"],getattr(x,"indexes",x),getattr(x,"values",""))
