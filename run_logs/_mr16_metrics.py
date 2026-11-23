import os, collections
from spinedb_api import DatabaseMapping, from_database
W={"05-14":100.81,"09-10":159.38,"12-24":104.81}
f=r"checkpoints\Investment_Results.3day_mr_ccslow_ccu_cap16_dac0.sqlite"
a=collections.Counter()
with DatabaseMapping("sqlite:///"+os.path.abspath(f)) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"]!="unit_flow": continue
        b=v["entity_byname"]; u=b[1]; key=None
        if u.startswith("CO2-injection") and b[2]=="atmosphere": key="stored_kt_"+u.replace("CO2-injection-","")
        elif u.startswith("methanation") and b[2].startswith("CH4"): key="methanation_GWh"
        elif u.startswith("DAC") and b[2].startswith("CO2"): key="DAC_kt"
        if not key: continue
        val=from_database(v["value"],v["type"])
        for i,x in zip(val.indexes,val.values):
            w=W.get(str(i)[5:10])
            if w: a[(str(i)[:4],key)]+=float(x)*w
for k,v in sorted(a.items()):
    if abs(v)>1e-3: print(k, round(v,1))
print("DAC total",round(sum(v for k,v in a.items() if k[1]=="DAC_kt"),3),"methanation total",round(sum(v for k,v in a.items() if k[1]=="methanation_GWh"),3))
