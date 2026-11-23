import glob, os, sys; sys.path.insert(0,"tools"); import postprocess as P
from spinedb_api import DatabaseMapping, from_database
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\*.sqlite")[0]
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    ents = {e["id"]: e for e in d.get_entity_items()}
    n = 0
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] in ("capacity_per_connection","connection_flow"):
            bn = ents[v["entity_id"]]["entity_byname"]
            if n < 6 or "CO2" in bn[2] and n < 12:
                x = from_database(v["value"], v["type"]); print(v["parameter_definition_name"], bn, type(x).__name__, str(x)[:200]); n += 1
