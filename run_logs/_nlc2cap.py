import os,re,sys,collections
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping, from_database
n="nb_ccslow_ccu_cap16_dac0"
inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; out=rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite"
with DatabaseMapping("sqlite:///"+os.path.abspath(inp)) as db:
    for cls in ["connection__from_node","connection__to_node"]:
        for v in db.get_parameter_value_items(entity_class_name=cls):
            if "CO2" in v["entity_byname"][0] and "NLC2" in v["entity_byname"][0] and v["parameter_definition_name"] in ("connection_capacity","connection_flow_cost"):
                print(cls, v["entity_byname"], v["parameter_definition_name"], v["alternative_name"], from_database(v["value"],v["type"]))
    for v in db.get_parameter_value_items(entity_class_name="connection"):
        if "CO2" in v["entity_byname"][0] and "NLC2" in v["entity_byname"][0]: print("conn",v["entity_byname"],v["parameter_definition_name"],from_database(v["value"],v["type"]))
mx=collections.defaultdict(float); tot=collections.defaultdict(float)
with DatabaseMapping("sqlite:///"+os.path.abspath(out)) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
        c,node,d=v["entity_byname"][1:4]
        if "CO2" in c and "NLC2" in c and d=="to_node":
            ts=from_database(v["value"],v["type"])
            for k,s in ts.items() if hasattr(ts,"items") else []:
                for t,x in zip(s.indexes,s.values):
                    y=str(t)[:4]; mx[(c,y)]=max(mx[(c,y)],x); tot[(c,y)]+=x
for k in sorted(mx): print(k, "max", round(mx[k],1), "sum", round(tot[k],1))
