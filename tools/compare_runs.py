"""Compare investment by category across two results DBs."""
import re, collections, sys
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

REGION = re.compile(r"_(BE|NL)C\d$")

def classify(t):
    l = t.lower()
    if "production-alternative" in l:      return "industry: clean process route"
    if "+cc" in l or "cal" in l or "mea" in l or "dea" in l or "oxy" in l:
        return "industry: CCS-equipped process"
    if l.startswith("dac"):                return "CO2 removal (DAC)"
    if "ref(h2)" in l or "smr" in l:       return "hydrogen production"
    if any(s in l for s in ("pem","aec","soec","diaphragm")): return "electrolysis"
    if "meoh" in l or "(bm)ft" in l or "nh3" in l:            return "e-fuels / green chemicals"
    if l.startswith("bio"):                return "bioenergy"
    if "solar" in l or "wind" in l:        return "renewables"
    if "heatpump" in l:                    return "electrification (heat pumps)"
    if "ocgt" in l or "ccgt" in l or "gas-boiler" in l:       return "unabated fossil"
    if "-dr_" in l:                        return "demand response"
    return "other"

def load(path):
    cat = collections.Counter()
    with DatabaseMapping("sqlite:///" + path) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"] != "units_invested":
                continue
            n = v["entity_name"].replace("default_report__", "").rstrip("_").replace("__realization", "")
            tech = REGION.sub("", n)
            val = from_database(v["value"], v["type"])
            try:
                for x in val.values:
                    x = float(x)
                    if x > 0:
                        cat[classify(tech)] += x
            except Exception:
                pass
    return cat

a = load(".spinetoolbox/items/investment_results/Investment_Results.6ts.sqlite")
b = load(".spinetoolbox/items/investment_results/Investment_Results.24h.sqlite")
ta, tb = sum(a.values()), sum(b.values())
keys = sorted(set(a) | set(b), key=lambda k: -(b.get(k,0)))
print("%-34s %9s %9s %9s %9s" % ("category", "9ts", "9ts%", "75ts", "75ts%"))
for k in keys:
    print("%-34s %9.2f %8.1f%% %9.2f %8.1f%%" % (k, a.get(k,0), 100*a.get(k,0)/ta, b.get(k,0), 100*b.get(k,0)/tb))
print("%-34s %9.2f %9s %9.2f" % ("TOTAL", ta, "", tb))
