"""Why is no wind built? Check entities, costs, caps and availability."""
import re, collections
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

mod = "sqlite:///checkpoints/Final_SpineOpt_Model.tiny.sqlite"
res = "sqlite:///.spinetoolbox/items/investment_results/Investment_Results.24h.sqlite"
REGION = re.compile(r"_(BE|NL)C\d$")

print("=== 1. wind/solar UNIT entities in the model ===")
with DatabaseMapping(mod) as db:
    units = [e["name"] for e in db.get_entity_items() if e["entity_class_name"] == "unit"]
    fams = collections.Counter()
    for u in units:
        l = u.lower()
        if "wind" in l or "solar" in l:
            fams[REGION.sub("", u)] += 1
    for k, n in sorted(fams.items()):
        print("   %-44s x%d" % (k, n))

print()
print("=== 2. cost / cap parameters per family ===")
KEYS = ["unit_investment_cost", "fom_cost", "capacity_per_unit",
        "investment_count_max_cumulative", "investment_count_initial_cumulative"]
with DatabaseMapping(mod) as db:
    data = collections.defaultdict(lambda: collections.defaultdict(list))
    for v in db.get_parameter_value_items():
        nm = v["entity_name"]; l = nm.lower()
        if not ("wind" in l or "solar" in l):
            continue
        p = v["parameter_definition_name"]
        if p not in KEYS:
            continue
        val = from_database(v["value"], v["type"])
        try:
            n = sum(float(x) for x in val.values) / max(1, len(val.values))
        except Exception:
            try: n = float(val)
            except Exception: continue
        data[REGION.sub("", nm)][p].append(n)
    for fam in sorted(data):
        d = data[fam]
        def f(p):
            if p not in d: return "       -"
            return "%8.4g" % (sum(d[p]) / len(d[p]))
        print("   %-40s capex=%s fom=%s cap/unit=%s max=%s init=%s" % (
            fam[:40], f("unit_investment_cost"), f("fom_cost"), f("capacity_per_unit"),
            f("investment_count_max_cumulative"), f("investment_count_initial_cumulative")))

print()
print("=== 3. what was actually built (24h run) ===")
with DatabaseMapping(res) as db:
    built = collections.defaultdict(float)
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"] != "units_invested":
            continue
        nm = v["entity_name"].replace("default_report__", "").rstrip("_").replace("__realization", "")
        l = nm.lower()
        if not ("wind" in l or "solar" in l):
            continue
        val = from_database(v["value"], v["type"])
        try:
            s = sum(float(x) for x in val.values)
        except Exception:
            continue
        built[REGION.sub("", nm)] += s
    for k, s in sorted(built.items(), key=lambda a: -a[1]):
        print("   %-44s %10.2f" % (k, s))
