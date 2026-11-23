import os, collections
from spinedb_api import DatabaseMapping, from_database
f=os.path.abspath(r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite")
agg=collections.Counter(); meth=collections.Counter()
with DatabaseMapping("sqlite:///"+f) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"]!="unit_flow": continue
        b=v["entity_byname"]; u,n,d=b[1],b[2],b[3]
        val=from_database(v["value"],v["type"])
        for i,x in zip(val.indexes,val.values):
            y=str(i)[:4]
            if n=="atmosphere": agg[(y,d)]+=float(x)
            if u.startswith("methanation") and n.startswith("CH4"): meth[y]+=float(x)
print(sorted(agg.items())); print(sorted(meth.items()))
