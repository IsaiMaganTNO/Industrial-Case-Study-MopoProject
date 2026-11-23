import os, collections
from spinedb_api import DatabaseMapping
for p in [r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite",
          r"runs\rp10_mr_noblend\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite"]:
    with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
        c = collections.Counter((v["entity_byname"][1], v["alternative_name"]) for v in m.get_parameter_value_items(entity_class_name="node__temporal_block"))
        print(os.path.basename(p)); [print("  ", k, n) for k, n in sorted(c.items())[:8]]
        print("   total", sum(c.values()))
