"""Correct the classifier bug: was 'wind-on-SP277' counted as solar?"""
import re
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database
REGION = re.compile(r"_(BE|NL)C\d$")
res = "sqlite:///.spinetoolbox/items/investment_results/Investment_Results.24h.sqlite"
tot = {}
with DatabaseMapping(res) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"] != "units_invested": continue
        nm = v["entity_name"].replace("default_report__","").rstrip("_").replace("__realization","")
        l = nm.lower()
        if "wind" not in l and "solar" not in l: continue
        val = from_database(v["value"], v["type"])
        try: s = sum(float(x) for x in val.values)
        except Exception: continue
        if s > 1e-9:
            tot[nm] = tot.get(nm, 0) + s
print("ALL non-zero wind/solar investments (24h run):")
for k, s in sorted(tot.items(), key=lambda a: -a[1]):
    print("   %-44s %10.2f" % (k[:44], s))
print()
print("wind total : %.2f" % sum(s for k,s in tot.items() if "wind" in k.lower()))
print("solar total: %.2f" % sum(s for k,s in tot.items() if "solar" in k.lower()))
