import os, collections
from spinedb_api import DatabaseMapping, from_database
p = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
    S = collections.defaultdict(set); cls = collections.Counter()
    for e in m.get_entity_items():
        bn = e["entity_byname"]
        if len(bn) > 1:
            for x in bn:
                if str(x).startswith("representative_period_") or x == "all_rps":
                    cls[(e["entity_class_name"], "all_rps" if x == "all_rps" else "rp")] += 1
                    if x != "all_rps": S[x].add(bn[0])
    print(dict(cls)); sets = list(S.values()); print("node sets identical across 9 blocks:", all(s == sets[0] for s in sets), len(sets[0]))
    cc = collections.Counter((v["entity_byname"][1][:26], str(from_database(v["value"], v["type"])), v["alternative_name"]) for v in m.get_parameter_value_items(entity_class_name="node__temporal_block"))
    print(cc.most_common(6))
    for v in m.get_parameter_value_items(entity_class_name="temporal_block", parameter_definition_name="representative_blocks_by_period"):
        print(v["entity_name"], [str(i) for i in from_database(v["value"], v["type"]).indexes])
