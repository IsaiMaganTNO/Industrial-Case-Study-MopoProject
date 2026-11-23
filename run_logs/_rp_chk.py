import os, sys; sys.path.insert(0, "tools")
from spinedb_api import DatabaseMapping, from_database
base = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input"
db = [f for f in os.listdir(base) if f.endswith(".sqlite")][0]; print(db)
with DatabaseMapping("sqlite:///" + os.path.abspath(os.path.join(base, db))) as m:
    for v in m.get_parameter_value_items():
        if v["entity_class_name"] == "temporal_block" or (v["entity_class_name"] == "model") or v["parameter_definition_name"] in ("storage_state_representative_map", "representative_blocks_by_period", "storage_state_interlaced_mapping", "is_longterm_storage"):
            x = from_database(v["value"], v["type"]); s = str(x).replace("\n", " ")
            print(v["entity_class_name"], v["entity_name"], v["parameter_definition_name"], s[:140])
