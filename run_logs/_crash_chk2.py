import os, collections
from spinedb_api import DatabaseMapping
p3 = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
with DatabaseMapping("sqlite:///" + os.path.abspath(p3)) as m:
    blk = collections.defaultdict(set)
    for e in m.get_entity_items(entity_class_name="node__temporal_block"):
        n, b = e["entity_byname"]; blk[b].add(n)
    rps = [b for b in blk if b.startswith("representative")]
    print({b: len(blk[b]) for b in sorted(blk)})
    same = all(blk[b] == blk[rps[0]] for b in rps); print("all rp same node set:", same)
    if not same:
        for b in rps: print(b, len(blk[b] - blk[rps[0]]), len(blk[rps[0]] - blk[b]))
    print("overlap rp & all_rps:", len(blk[rps[0]] & blk["all_rps"]), " rp & ops:", len(blk[rps[0]] & blk["operations_y2030"]))
