import os, collections
from spinedb_api import DatabaseMapping, from_database
p = r"runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
    c = collections.Counter()
    for v in m.get_parameter_value_items(entity_class_name="node"):
        n = v["parameter_definition_name"]
        if "state" in n or "storage" in n or "longterm" in n or "representative" in n:
            c[(n, str(from_database(v["value"], v["type"]))[:25] if n.endswith(("method", "longterm", "has_state")) else "")] += 1
    for k, x in sorted(c.items()): print(k, x)
