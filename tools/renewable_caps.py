"""Renewable investment caps per region and per investment year."""
import re, collections
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

mod = "sqlite:///checkpoints/Final_SpineOpt_Model.tiny.sqlite"
KEYS = ["investment_count_max_cumulative",
        "investment_count_total_max_cumulative",
        "investment_count_initial_cumulative",
        "investment_count_fix_new"]

def series(val):
    try:
        return [(str(i)[:4], float(x)) for i, x in zip(val.indexes, val.values)]
    except Exception:
        try:
            return [("all", float(val))]
        except Exception:
            return []

rows = collections.defaultdict(dict)
with DatabaseMapping(mod) as db:
    for v in db.get_parameter_value_items():
        p = v["parameter_definition_name"]
        if p not in KEYS:
            continue
        nm = v["entity_name"]
        l = nm.lower()
        if not ("wind" in l or "solar" in l):
            continue
        if "__" in nm:          # skip unit__node flow entities
            continue
        rows[nm][p] = series(from_database(v["value"], v["type"]))

def fmt(s):
    if not s:
        return "        -"
    d = dict(s)
    return " ".join("%s:%s" % (y, ("%.4g" % d[y]) if y in d else "-")
                    for y in ("2030", "2040", "2050") if y in d) or ("%.4g" % s[0][1])

for nm in sorted(rows):
    d = rows[nm]
    print("%-38s max[%s]" % (nm[:38], fmt(d.get("investment_count_max_cumulative"))))
    if "investment_count_total_max_cumulative" in d:
        print("%-38s   TOTAL cap [%s]" % ("", fmt(d["investment_count_total_max_cumulative"])))
    if "investment_count_initial_cumulative" in d:
        print("%-38s   initial   [%s]" % ("", fmt(d["investment_count_initial_cumulative"])))
