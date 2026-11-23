import sqlite3
from spinedb_api import DatabaseMapping, from_database
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
with DatabaseMapping("sqlite:///"+db) as m:
    ents=[e["name"] for e in m.get_entity_items(entity_class_name="unit") if "nuclear-3" in e["name"]]
    print("nuclear-3 units:",len(ents)); print(sorted(ents)[:25])
