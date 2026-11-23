import os,re,collections
from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
CAR=["elec","CH4","H2","CO2","HC","MeOH","bio"]
N=re.compile(r"^(%s)_((BE|NL)C\d)$"%"|".join(CAR))
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    nodes={e["name"] for e in db.get_entity_items(entity_class_name="node") if N.match(e["name"])}
    print("network nodes:",len(nodes))
    pv=collections.Counter(); 
    for v in db.get_parameter_value_items():
        bn=v["entity_byname"]
        if any(x in nodes for x in bn): pv[(v["entity_class_name"],v["parameter_definition_name"],v["type"])]+=1
    for k,c in sorted(pv.items()): print(" ",k,c)
    rc=collections.Counter(e["entity_class_name"] for e in db.get_entity_items() if any(x in nodes for x in e["entity_byname"]))
    print("relationships:",dict(rc))
    print("node-level params on other zone nodes (storage etc.) not needed for merge")
