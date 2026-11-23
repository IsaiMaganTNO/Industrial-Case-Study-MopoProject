import os, collections
from spinedb_api import DatabaseMapping, from_database
p = r"runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
    c = collections.Counter(); ex = {}
    for v in m.get_parameter_value_items():
        n = v["parameter_definition_name"]
        if "penalty" in n or "slack" in n:
            c[(v["entity_class_name"], n)] += 1; ex.setdefault((v["entity_class_name"], n), (v["entity_name"], str(from_database(v["value"], v["type"]))[:30]))
    for k, x in c.items(): print(k, x, ex[k])
    sf = [v["entity_name"] for v in m.get_parameter_value_items(entity_class_name="node", parameter_definition_name="storage_state_fix")]
    print("state_fix nodes sample:", sorted(set(sf))[:10])
