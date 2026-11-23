import os
from spinedb_api import DatabaseMapping, from_database
for f in [r"runs\3day_nb_ccslow\output", r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite"]:
    if os.path.isdir(f): f=os.path.join(f,[x for x in os.listdir(f) if x.endswith(".sqlite")][0])
    with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"] in ("node_state_longterm","storages_invested_available") and "atmosphere" in v["entity_byname"]:
                val=from_database(v["value"],v["type"])
                print(os.path.basename(f), v["parameter_definition_name"], [(str(i)[:4],round(float(x),3)) for i,x in zip(val.indexes,val.values)][:12])
