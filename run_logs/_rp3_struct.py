import os, collections
from spinedb_api import DatabaseMapping, from_database
p = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
    c = collections.Counter()
    rel_ids = set()
    for e in m.get_entity_items():
        bn = e["entity_byname"]
        if len(bn) > 1 and any(str(x).startswith("representative_period_2050_1") for x in bn):
            c[e["entity_class_name"]] += 1; rel_ids.add(e["id"])
    print("relations with rp_2050_1:", dict(c))
    for g in m.get_entity_group_items():
        if "representative" in g["member_name"] or g["group_name"] == "all_rps": c["group:" + g["group_name"]] += 1
    print({k: v for k, v in c.items() if k.startswith("group")})
    pv = collections.Counter(v["parameter_definition_name"] for v in m.get_parameter_value_items() if v["entity_id"] in rel_ids)
    print("params on those relations:", dict(pv))
    for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
        if v["entity_name"].startswith("representative_period_2050_1") or (v["entity_name"] == "operations_y2050" and v["parameter_definition_name"] == "representative_blocks_by_period"):
            x = from_database(v["value"], v["type"])
            print(v["entity_name"], v["parameter_definition_name"], v["alternative_name"], v["type"], (list(map(str, x.indexes)), [list(r.values) for r in x.values]) if v["type"] == "map" else x)
    print("all_rps params:", [(v["parameter_definition_name"], str(from_database(v["value"], v["type"]))) for v in m.get_parameter_value_items(entity_class_name="temporal_block") if v["entity_name"] == "all_rps"])
    for e in m.get_entity_items(entity_class_name="model__default_temporal_block"): print("default tb:", e["entity_byname"])
