import os, collections
from spinedb_api import DatabaseMapping, from_database
for f in [r"runs\3day_nb_ccslow\output\Investment_Results.3day_nb_ccslow.sqlite", r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite"]:
    a=collections.Counter(); inv=collections.Counter()
    with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
        for v in db.get_parameter_value_items():
            b=v["entity_byname"]; p=v["parameter_definition_name"]
            if len(b)>1 and b[1].startswith("DAC") and p in ("unit_flow","units_invested_available"):
                val=from_database(v["value"],v["type"])
                for i,x in zip(val.indexes,val.values):
                    if p=="unit_flow": a[(str(i)[:4],b[2].split("_")[0],b[3])]+=float(x)
                    else: inv[(str(i)[:4],b[1])]+=float(x)
    print(os.path.basename(f)); print("  flows",{k:round(v,2) for k,v in a.items() if abs(v)>1e-6}); print("  avail",{k:round(v,3) for k,v in inv.items() if abs(v)>1e-6})
