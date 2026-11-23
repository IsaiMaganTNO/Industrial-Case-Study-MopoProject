import os, collections
from spinedb_api import DatabaseMapping, from_database
W={"05-14":100.81,"09-10":159.38,"12-24":104.81}
def wk(t):
    s=str(t); 
    for k,w in W.items():
        if s[5:10]==k: return w
    return None
for tag,f in [("cap125",r"checkpoints\Investment_Results.3day_nb_ccslow_ccu_cap125.sqlite"),("ccu",r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite")]:
    net=collections.Counter(); raw=collections.Counter(); miss=collections.Counter()
    with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"]!="unit_flow": continue
            b=v["entity_byname"]
            if b[2]!="atmosphere": continue
            sg=1 if b[3]=="to_node" else -1
            val=from_database(v["value"],v["type"])
            for i,x in zip(val.indexes,val.values):
                y=str(i)[:4]; w=wk(i)
                raw[y]+=sg*float(x)
                if w is None: miss[str(i)[5:10]]+=1
                else: net[y]+=sg*float(x)*w
    print(tag,"raw net",{k:round(v,2) for k,v in sorted(raw.items())})
    print(tag,"weighted net",{k:round(v,1) for k,v in sorted(net.items())},"unmatched",dict(miss))

