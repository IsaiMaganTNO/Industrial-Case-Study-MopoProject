import os
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database
p = os.path.join(".spinetoolbox", "items", "final_spineopt_model", "Final_SpineOpt_Model.sqlite")
with DatabaseMapping("sqlite:///" + os.path.abspath(p)) as db:
    b = {}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"] != "temporal_block":
            continue
        n = str(v["entity_name"])
        if not n.startswith("representative"):
            continue
        pn = v["parameter_definition_name"]
        if pn in ("block_start", "block_end", "weight"):
            val = from_database(v["value"], v["type"])
            b.setdefault(n, {})[pn] = getattr(val, "value", val)
    tot = {}
    for n in sorted(b):
        d = b[n]
        y = str(d.get("block_start"))[:4]
        w = float(d.get("weight", 0))
        tot[y] = tot.get(y, 0.0) + w
        print("%-32s %s -> %s  w=%.4f" % (n, str(d.get("block_start"))[:10],
                                          str(d.get("block_end"))[:10], w))
    print("")
    for y in sorted(tot):
        print("  weights sum %s = %.6f" % (y, tot[y]))
