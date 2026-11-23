import os, collections
from spinedb_api import DatabaseMapping, from_database
f=r"checkpoints\Investment_Results.3day_nb_ccslow_ccu_cap125.sqlite"
avail=collections.defaultdict(float); flow=collections.Counter()
with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
    for v in db.get_parameter_value_items():
        p=v["parameter_definition_name"]; b=v["entity_byname"]
        if p=="units_invested_available":
            val=from_database(v["value"],v["type"]); avail[b[1]]=max([float(x) for x in val.values]+[0])
        elif p=="unit_flow" and b[3]=="to_node":
            val=from_database(v["value"],v["type"]); flow[b[1]]+=sum(abs(float(x)) for x in val.values)
sus=collections.Counter()
for u,fl in flow.items():
    if fl>1e-3 and avail.get(u,0)<1e-6: sus[u.rsplit("_",1)[0]]+=1
print("units with output flow but zero invested capacity, by family:")
for k,v in sorted(sus.items()): print(f"  {k:50s} {v}")
