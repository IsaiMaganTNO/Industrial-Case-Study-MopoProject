import os, collections
from spinedb_api import DatabaseMapping
p3 = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
p10 = r"runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p3)) as m:
    blk = collections.defaultdict(set)
    for e in m.get_entity_items(entity_class_name="node__temporal_block"): blk[e["entity_byname"][1]].add(e["entity_byname"][0])
rp_nodes = blk["representative_period_2030_1"]; all_nodes = blk["all_rps"]
with DatabaseMapping("sqlite:///" + os.path.abspath(p10)) as m:
    have = {tuple(e["entity_byname"]) for e in m.get_entity_items(entity_class_name="node__temporal_block")}
    blocks = sorted(e["name"] for e in m.get_entity_items(entity_class_name="temporal_block") if e["name"].startswith("representative_period"))
    print("new blocks", len(blocks)); n = 0
    for b in blocks:
        for nd in rp_nodes:
            if (nd, b) not in have:
                _, err = m.add_entity_item(entity_class_name="node__temporal_block", entity_byname=(nd, b)); n += 1
                if err: raise RuntimeError(err)
    for nd in all_nodes:
        if (nd, "all_rps") not in have:
            _, err = m.add_entity_item(entity_class_name="node__temporal_block", entity_byname=(nd, "all_rps")); n += 1
            if err: raise RuntimeError(err)
    m.commit_session("relink nodes to 10-day representative blocks"); print("added", n)
with DatabaseMapping("sqlite:///" + os.path.abspath(p10)) as m:
    c = collections.Counter(e["entity_byname"][1] for e in m.get_entity_items(entity_class_name="node__temporal_block"))
    print({k: v for k, v in sorted(c.items())})
