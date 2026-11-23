import os,collections
from spinedb_api import DatabaseMapping
with DatabaseMapping("sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mr_fix.sqlite")) as db:
    c=collections.Counter((v["entity_class_name"],v["parameter_definition_name"]) for v in db.get_parameter_value_items())
for k,v in sorted(c.items()): print(k,v)
