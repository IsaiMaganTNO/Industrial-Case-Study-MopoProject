"""Print the objective cost breakdown of a SpineOpt results DB.

Objective terms are stored as time series (one value per investment period),
not scalars, so they must be summed over their values.
"""
import sys
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

path = sys.argv[1] if len(sys.argv) > 1 else ".spinetoolbox/items/investment_results/Investment_Results.sqlite"


def total_of(val):
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        pass
    vals = getattr(val, "values", None)
    if vals is not None:
        try:
            return float(sum(vals))
        except Exception:
            return None
    return None


tot = {}
with DatabaseMapping("sqlite:///" + path) as db:
    for v in db.get_parameter_value_items():
        n = v["parameter_definition_name"]
        if not (n.startswith("objective_") or n == "total_costs"):
            continue
        f = total_of(from_database(v["value"], v["type"]))
        if f is None:
            print("  (could not parse %s)" % n)
            continue
        tot[n] = tot.get(n, 0.0) + f

total = tot.get("total_costs") or sum(x for k, x in tot.items() if k != "total_costs")
print("%-40s %18s %8s" % ("term", "value", "share"))
for k, x in sorted(tot.items(), key=lambda a: -a[1]):
    print("%-40s %18.2f %7.2f%%" % (k, x, 100 * x / total if total else 0.0))
