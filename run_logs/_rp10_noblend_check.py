import os, collections
from spinedb_api import DatabaseMapping, from_database
A = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
B = r"runs\rp10_mr_noblend\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite"
def snap(p):
    with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
        rp = lambda bn: any(str(x).startswith("representative_period_") for x in bn)
        ents = {(e["entity_class_name"], e["entity_byname"]) for e in m.get_entity_items() if not rp(e["entity_byname"])}
        pvs = {(v["entity_class_name"], v["entity_byname"], v["parameter_definition_name"], v["alternative_name"]): bytes(v["value"]) for v in m.get_parameter_value_items()
               if not rp(v["entity_byname"]) and v["parameter_definition_name"] != "representative_blocks_by_period"}
        blocks = {}
        for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
            if v["entity_name"].startswith("representative_period_"): blocks.setdefault(v["entity_name"], {})[v["parameter_definition_name"]] = from_database(v["value"], v["type"])
        links = collections.Counter(e["entity_byname"][1] for e in m.get_entity_items(entity_class_name="node__temporal_block"))
        cyc = collections.Counter(v["entity_byname"][1] for v in m.get_parameter_value_items(entity_class_name="node__temporal_block"))
        grp = sum(1 for g in m.get_entity_group_items() if g["group_name"] == "all_rps")
        maps = {v["entity_name"]: from_database(v["value"], v["type"]) for v in m.get_parameter_value_items(entity_class_name="temporal_block", parameter_definition_name="representative_blocks_by_period")}
        scen = [(s["scenario_name"], s["alternative_name"], s["rank"]) for s in m.get_scenario_alternative_items()]
        return ents, pvs, blocks, links, cyc, grp, maps, scen
a, b = snap(A), snap(B)
print("non-temporal entities identical:", a[0] == b[0], len(a[0]))
print("non-temporal parameter values identical:", a[1] == b[1], len(a[1]))
print("scenario/alternatives identical:", a[7] == b[7])
print("blocks:", len(a[2]), "->", len(b[2]), "| all_rps members:", a[5], "->", b[5])
print("node links per block 3d:", set(a[3].values()), "10d:", set(v for k, v in b[3].items() if k.startswith("rep")), "| all_rps links:", a[3]["all_rps"], b[3]["all_rps"])
print("cyclic_condition values per block 3d:", set(a[4].values()), "10d:", set(b[4].values()))
for y in ("2030", "2040", "2050"):
    bl = {k: v for k, v in b[2].items() if f"_{y}_" in k}
    print(y, "n", len(bl), "weight sum", round(sum(v["weight"] for v in bl.values()), 3),
          "idx", sorted(int(v["representative_block_index"]) for v in bl.values()))
    mp = b[6][f"operations_y{y}"]; row = list(mp.values[0].values)
    print("   map rows", len(mp.indexes), "index", str(mp.indexes[0]), "row sum", round(sum(row), 6), "nonzero cols", [i for i, w in enumerate(row) if w > 0])
for n in sorted(b[2], key=lambda s: (s[:26], int(s.split("_")[-1])))[:10]:
    v = b[2][n]; print(n, v["block_start"], "->", v["block_end"], round(v["weight"], 2), v["resolution"])
