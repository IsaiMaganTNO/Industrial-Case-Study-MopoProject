import os, collections
from spinedb_api import DatabaseMapping, from_database
for tag, p in [("10d", r"runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite"),
               ("3d", r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite")]:
    with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
        print("==", tag)
        for v in m.get_parameter_value_items(entity_class_name="connection", entity_name="AT_CH4_DE"):
            print("  ", v["parameter_definition_name"], v["alternative_name"], str(from_database(v["value"], v["type"]))[:60])
        c = collections.Counter(v["parameter_definition_name"] for v in m.get_parameter_value_items(entity_class_name="connection") if "delay" in v["parameter_definition_name"])
        print("  delay params:", dict(c))
        tb = collections.Counter((e["entity_class_name"], e["entity_byname"][-1]) for e in m.get_entity_items() if e["entity_class_name"] in ("node__temporal_block", "model__default_temporal_block", "units_on__temporal_block", "model__default_investment_temporal_block"))
        print("  block links:", dict(tb) if len(tb) < 15 else list(tb.items())[:15])
        for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
            if not v["entity_name"].startswith("representative") and v["parameter_definition_name"] in ("resolution", "block_start", "block_end"):
                print("  ", v["entity_name"], v["parameter_definition_name"], v["alternative_name"], str(from_database(v["value"], v["type"]))[:60])
