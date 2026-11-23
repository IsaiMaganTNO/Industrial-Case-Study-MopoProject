import os,re,collections
from spinedb_api import DatabaseMapping, from_database
import sys; sys.path.insert(0,"tools"); import postprocess as PP
w=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
print("wmap sample",list(w.items())[:3] if isinstance(w,dict) else type(w))
tot=collections.defaultdict(float)
with DatabaseMapping("sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mr_fix.sqlite")) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
        conn,node,d=v["entity_byname"][1],v["entity_byname"][2],v["entity_byname"][3]
        if not node.startswith("CH4"): continue
        a=re.findall(r"(?:^|_)([A-Z]{2})(?:C\d|\b|$)",conn)
        val=from_database(v["value"],v["type"])
        for t,x in zip(val.indexes,val.values):
            y=str(t)[:4]; tot[(conn,node,d,y)]+=float(x)
# raw sums (unweighted MW over timesteps)
cb=collections.defaultdict(float)
for (c,n,d,y),s in tot.items():
    cc=set(re.findall(r"CH4_([A-Z]{2})",c))
    nc=n[4:6]
    if len(cc)>1 and d=="to_node": cb[(c,n,y)]+=s
for k in sorted(cb): 
    if abs(cb[k])>1: print(k, round(cb[k]))
