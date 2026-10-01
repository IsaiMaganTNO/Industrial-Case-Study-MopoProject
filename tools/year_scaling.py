"""Is the representative day scaled up to a full year?
Compare CO2 into atmosphere against the annual budget, and check
the operational timestep duration that does the scaling."""
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

mod = "sqlite:///checkpoints/Final_SpineOpt_Model.tiny.sqlite"
res = "sqlite:///.spinetoolbox/items/investment_results/Investment_Results.24h.sqlite"

print("=== operational block duration (this is what scales a day to a year) ===")
with DatabaseMapping(mod) as db:
    info = {}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"] != "temporal_block": continue
        if v["parameter_definition_name"] in ("resolution","block_start","block_end"):
            info.setdefault(v["entity_name"], {})[v["parameter_definition_name"]] = from_database(v["value"], v["type"])
    for b in sorted(info):
        d = info[b]
        s,e,r = d.get("block_start"), d.get("block_end"), d.get("resolution")
        if not (s and e and r): continue
        hrs = (e.value - s.value).total_seconds()/3600
        step = ((s.value + r.value) - s.value).total_seconds()/3600
        print("  %-30s span=%7.0f h  step=%7.0f h  -> %.0f timestep(s)" % (b[:30], hrs, step, hrs/step))

print()
print("=== atmosphere: budget vs realised state (24h run) ===")
with DatabaseMapping(mod) as db:
    for v in db.get_parameter_value_items():
        if v["entity_name"] != "atmosphere": continue
        if v["parameter_definition_name"] not in ("storage_investment_count_max_cumulative","storage_state_max"): continue
        val = from_database(v["value"], v["type"])
        try:
            print("  %-42s %s" % (v["parameter_definition_name"],
                  ", ".join("%s=%.5g" % (str(i)[:10], float(x)) for i,x in zip(val.indexes, val.values))))
        except Exception:
            print("  %-42s %s" % (v["parameter_definition_name"], val))

with DatabaseMapping(res) as db:
    for v in db.get_parameter_value_items():
        if "atmosphere" not in v["entity_name"]: continue
        if v["parameter_definition_name"] != "node_state_longterm": continue
        val = from_database(v["value"], v["type"])
        pairs = [(str(i)[:10], float(x)) for i,x in zip(val.indexes, val.values)]
        print("  realised node_state_longterm:", ", ".join("%s=%.5g" % p for p in pairs[:6]))
