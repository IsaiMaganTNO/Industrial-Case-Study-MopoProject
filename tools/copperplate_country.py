r"""Copper-plate NL+BE: make every intra-country zone-to-zone connection unconstrained,
free and without investment. Zones stay as nodes; each country behaves as one node.
Usage: python tools/copperplate_country.py SRC DST
Removes on intra-country connections (pattern <CC>Cn_<carrier>_<CC>Cm, same CC):
  capacity_per_connection, connection_flow_cost (from/to_node),
  connection_investment_cost, investment_count_* , lifetime_* (connection).
Keeps fix_ratio_out_in_connection_flow = 1.0 (lossless) and all other data.
"""
import os, re, sys, shutil, collections
from spinedb_api import DatabaseMapping
src, dst = sys.argv[1], sys.argv[2]
if os.path.exists(dst): sys.exit(f"exists: {dst}")
shutil.copyfile(src, dst)
I = re.compile(r"^((BE|NL)C\d)_(\w+?)_((BE|NL)C\d)$")
DROP = {"capacity_per_connection", "connection_flow_cost", "connection_investment_cost",
        "investment_count_fix_cumulative", "investment_count_fix_new", "investment_count_initial_cumulative",
        "investment_count_max_cumulative", "lifetime_constraint_sense", "lifetime_economic", "lifetime_technical"}
with DatabaseMapping("sqlite:///" + os.path.abspath(dst)) as db:
    intra = {e["name"] for e in db.get_entity_items(entity_class_name="connection")
             if (m := I.match(e["name"])) and m.group(2) == m.group(5)}
    rm = collections.Counter(); keep = collections.Counter()
    for v in db.get_parameter_value_items():
        bn = v["entity_byname"]
        if not bn or bn[0] not in intra: continue
        k = (v["entity_class_name"], v["parameter_definition_name"])
        if v["parameter_definition_name"] in DROP:
            db.remove_item("parameter_value", v["id"]); rm[k] += 1
        else: keep[k] += 1
    db.commit_session("copperplate NL+BE intra-country connections")
print("intra-country connections:", len(intra))
print("removed:", dict(rm), "total", sum(rm.values()))
print("kept:", dict(keep))
