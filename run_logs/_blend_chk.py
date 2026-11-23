import os
from spinedb_api import DatabaseMapping, from_database
for tag, p in [("3day MR", r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"),
               ("3day IC1", r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite")]:
    with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as m:
        for v in m.get_parameter_value_items(entity_class_name="temporal_block", parameter_definition_name="representative_blocks_by_period"):
            if v["entity_name"] != "operations_y2050": continue
            x = from_database(v["value"], v["type"]); rows = [list(r.values) for r in x.values]
            nz = [[w for w in r if w > 1e-9] for r in rows]
            print(tag, v["alternative_name"], "days", len(rows), "rows with >1 rep:", sum(len(r) > 1 for r in nz), "example:", [[round(w, 3) for w in r] for r in nz if r][:1], [[round(w, 3) for w in r] for r in nz if r][100:101], "empty rows", sum(1 for r in nz if not r), "nonzero cols", sorted({i for r in rows for i, w in enumerate(r) if w > 1e-9}))
        lim = [v for v in m.get_parameter_value_items(entity_class_name="connection") if v["parameter_definition_name"] in ("candidate_connections", "connection_investment_count_max_cumulative", "investment_count_max_cumulative")]
        print(tag, "connection limit params:", sorted({(v["parameter_definition_name"], v["alternative_name"]) for v in lim}))
        for v in lim[:4]: print("  ", v["entity_name"], v["alternative_name"], str(from_database(v["value"], v["type"]))[:80])
