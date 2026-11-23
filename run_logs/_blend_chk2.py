import os
from spinedb_api import DatabaseMapping, from_database
p = r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
    for v in m.get_parameter_value_items(entity_class_name="temporal_block", parameter_definition_name="representative_blocks_by_period"):
        if v["entity_name"] == "operations_y2050": x = from_database(v["value"], v["type"]); print("map index:", list(x.indexes))
    P = {}
    for v in m.get_parameter_value_items(entity_class_name="connection"):
        n = v["entity_name"]
        if "_elec_" in n or "elec" in n.lower():
            P.setdefault(n, {})[v["parameter_definition_name"]] = str(from_database(v["value"], v["type"]))[:40]
    for n in sorted(P)[:8]: print(n, P[n])
    print(len(P), "elec connections")
