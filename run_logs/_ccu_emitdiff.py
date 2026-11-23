import os, collections, sys
from spinedb_api import DatabaseMapping, from_database
res={}
for tag,f in [("old",r"runs\3day_nb_ccslow\output\Investment_Results.3day_nb_ccslow.sqlite"),("ccu",r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite")]:
    a=collections.Counter()
    with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"]!="unit_flow": continue
            b=v["entity_byname"]
            if b[2]!="atmosphere": continue
            val=from_database(v["value"],v["type"])
            s=sum(float(x) for i,x in zip(val.indexes,val.values) if str(i).startswith("2050"))
            a[(b[1].rsplit("_",1)[0],b[3])]+=s
    res[tag]=a
keys=set(res["old"])|set(res["ccu"])
for k in sorted(keys,key=lambda k:-abs(res["ccu"][k]-res["old"][k]))[:20]:
    print(f"{k[0]:45s} {k[1]:9s} old={res['old'][k]:9.3f} ccu={res['ccu'][k]:9.3f}")
