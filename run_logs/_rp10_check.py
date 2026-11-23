import os
from spinedb_api import DatabaseMapping, from_database
db = os.path.abspath(r"runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite")
with DatabaseMapping("sqlite:///" + db) as m:
    B = {}
    for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
        n = v["entity_name"]; x = from_database(v["value"], v["type"])
        if n.startswith("representative_period"): B.setdefault(n, {})[(v["parameter_definition_name"], v["alternative_name"])] = getattr(x, "value", x)
        elif v["parameter_definition_name"] == "representative_blocks_by_period":
            print(n, v["alternative_name"], "map len", len(x.indexes), "first row sum", round(sum(x.values[0].values), 3))
    print("n blocks", len(B))
    idx = sorted(int(b[("representative_block_index", "wy2009")]) for b in B.values()); print("indexes", idx)
    for y in ("2030", "2040", "2050"):
        ws = [b[("weight", "wy2009")] for n, b in B.items() if f"_{y}_" in n]; print(y, len(ws), "weight sum", round(sum(ws), 1))
    for n in sorted(B)[:3]: print(n, B[n][("block_start", "wy2009")], B[n][("block_end", "wy2009")])
    print("scenarios:", [(s["name"]) for s in m.get_scenario_items()])
    print("wy2009 in scenario:", [sa["alternative_name"] for sa in m.get_scenario_alternative_items()].count("wy2009"))
