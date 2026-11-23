import os,re,collections,hashlib
from spinedb_api import DatabaseMapping
I=re.compile(r"^((BE|NL)C\d)_(\w+?)_((BE|NL)C\d)$")
def load(p):
    d={}
    with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
        ents=collections.Counter(e["entity_class_name"] for e in db.get_entity_items())
        for v in db.get_parameter_value_items():
            d[(v["entity_class_name"],v["entity_byname"],v["parameter_definition_name"],v["alternative_name"])]=hashlib.md5(v["value"] or b"").hexdigest()+v["type"]
        sc=[(s["name"],tuple(x["alternative_name"] for x in sorted(db.get_scenario_alternative_items(scenario_name=s["name"]),key=lambda x:x["rank"]))) for s in db.get_scenario_items()]
    return d,ents,sc
A,ea,sa=load(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
B,eb,sb=load(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_cp.sqlite")
print("entities identical:",ea==eb, "scenarios identical:",sa==sb)
added=set(B)-set(A); changed=[k for k in A.keys()&B.keys() if A[k]!=B[k]]; removed=set(A)-set(B)
print("added",len(added),"changed",len(changed),"removed",len(removed))
bad=[k for k in removed if not ((m:=I.match(k[1][0])) and m.group(2)==m.group(5))]
print("removed NOT on intra-country connections:",len(bad))
print("removed by (class,param):",collections.Counter((k[0],k[2]) for k in removed).most_common())
