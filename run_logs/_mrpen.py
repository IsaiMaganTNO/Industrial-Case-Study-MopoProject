import sys, os
sys.path.insert(0,"tools")
from spinedb_api import DatabaseMapping, from_database
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
tot={}
with DatabaseMapping(url) as db:
    for v in db.get_parameter_value_items():
        if v["entity_class_name"]!="report__model": continue
        p=v["parameter_definition_name"]
        if not p.startswith("objective"): continue
        val=from_database(v["value"],v["type"])
        s=0.0
        for x in getattr(val,"values",[]):
            try: s+=float(getattr(x,"value",x))
            except Exception: pass
        tot[p]=s
for k in sorted(tot, key=lambda k:-abs(tot[k])):
    print(f"  {k:42s} {tot[k]:18,.4f}")
pen=sum(v for k,v in tot.items() if "penalt" in k.lower())
print()
print(f"PENALTIES TOTAL = {pen:,.6f}  ->", "PASS" if abs(pen)<1e-6 else "*** FAIL ***")
