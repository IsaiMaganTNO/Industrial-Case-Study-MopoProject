import os, collections, sqlite3
from spinedb_api import DatabaseMapping, from_database
W={"05-14":100.81,"09-10":159.38,"12-24":104.81}
inp=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap125.sqlite")
print("DAC_NLC1 links:",[n for (n,) in inp.execute("select name from entity where name like '%DAC\\_NLC1%' escape '\\'")])
f=r"checkpoints\Investment_Results.3day_nb_ccslow_ccu_cap125.sqlite"
sink=collections.Counter(); dac=collections.Counter()
with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"]!="unit_flow": continue
        b=v["entity_byname"]; u,n,d=b[1],b[2],b[3]
        val=from_database(v["value"],v["type"])
        s=sum(float(x)*W.get(str(i)[5:10],0) for i,x in zip(val.indexes,val.values) if str(i).startswith("2050"))
        if abs(s)<1: continue
        if n.startswith("CO2_") and d=="from_node": sink[u.rsplit("_",1)[0]]+=s
        if u.startswith("DAC"): dac[(n.split("_")[0],d)]+=s
print("DAC 2050:",{k:round(v,1) for k,v in dac.items()})
print("CO2 consumers 2050 (kt):",{k:round(v,1) for k,v in sorted(sink.items(),key=lambda kv:-kv[1])})
