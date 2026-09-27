"""Group units_invested into decarbonisation categories."""
import re, collections
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

res = "sqlite:///.spinetoolbox/items/investment_results/Investment_Results.sqlite"
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

cat = collections.defaultdict(lambda: collections.Counter())
with DatabaseMapping(res) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"] != "units_invested":
            continue
        n = v["entity_name"].replace("default_report__", "").rstrip("_")
        n = n.replace("__realization", "")
        tech = REGION.sub("", n)
        val = from_database(v["value"], v["type"])
        try:
            for i, x in zip(val.indexes, val.values):
                x = float(x)
                if x > 0:
                    cat[classify(tech)][str(i)[:4]] += x
        except Exception:
            pass

rows = sorted(cat.items(), key=lambda a: -sum(a[1].values()))
grand = sum(sum(c.values()) for _, c in rows)
print("%-34s %8s %8s %8s %9s %7s" % ("category", "2030", "2040", "2050", "TOTAL", "share"))
for k, c in rows:
    t = sum(c.values())
    print("%-34s %8.2f %8.2f %8.2f %9.2f %6.1f%%" % (k, c.get("2030",0), c.get("2040",0), c.get("2050",0), t, 100*t/grand))
print("%-34s %8s %8s %8s %9.2f" % ("TOTAL", "", "", "", grand))
