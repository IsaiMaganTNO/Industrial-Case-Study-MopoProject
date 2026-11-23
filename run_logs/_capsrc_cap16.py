import os, collections
from spinedb_api import DatabaseMapping, from_database
W={"05-14":100.81,"09-10":159.38,"12-24":104.81}
for tag,f in [("old",r"runs\3day_nb_ccslow\output\Investment_Results.3day_nb_ccslow.sqlite"),("cap125",r"checkpoints\Investment_Results.3day_nb_ccslow_ccu_cap16_dac0.sqlite")]:
    src=collections.Counter()
    with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"]!="unit_flow": continue
            b=v["entity_byname"]
            if not(b[2].startswith("CO2_") and b[3]=="to_node"): continue
            val=from_database(v["value"],v["type"])
            for i,x in zip(val.indexes,val.values):
                w=W.get(str(i)[5:10])
                if w and float(x)>0: src[(str(i)[:4],b[1].rsplit("_",1)[0])]+=float(x)*w/1e3
    for y in ("2030","2041","2050"):
        items={k[1]:round(v,2) for k,v in src.items() if k[0]==y and v>0.01}
        print(tag,y,"total",round(sum(items.values()),2),"Mt",dict(sorted(items.items(),key=lambda kv:-kv[1])))

