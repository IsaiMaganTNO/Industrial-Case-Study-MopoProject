import glob, os
from spinedb_api import DatabaseMapping
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\*.sqlite")[0]
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    s = {(v["entity_class_name"], v["parameter_definition_name"]) for v in d.get_parameter_value_items()}
for x in sorted(s): print(x)
