import sys, os
sys.path.insert(0,"tools")
from postprocess import load_weights
from spinedb_api import DatabaseMapping, from_database
import pandas as pd
wmap=load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_co2bidir.sqlite")
rows=[]
with DatabaseMapping(url) as db:
    ents={e["id"]:e for e in db.get_entity_items()}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"]!="report__unit__node__direction__stochastic_scenario": continue
        if v["parameter_definition_name"]!="unit_flow": continue
        e=ents.get(v["entity_id"]); bn=e["entity_byname"] if e else ()
        if len(bn)<4: continue
        unit,node,direc=bn[1],bn[2],bn[3]
        if not node.startswith("CH4_"): continue
        val=from_database(v["value"],v["type"])
        for idx,x in zip(getattr(val,"indexes",[]),getattr(val,"values",[])):
            ts=pd.Timestamp(str(idx)); w=wmap.get(ts.strftime("%Y-%m-%d"))
            if w is None: continue
            try: xv=float(getattr(x,"value",x))
            except Exception: continue
            rows.append((unit,node,direc,ts.year,xv*w))
df=pd.DataFrame(rows,columns=["unit","node","dir","year","val"])
df.to_pickle(r"run_logs\ch4units.pkl")
df["tech"]=df.unit.str.rsplit("_",n=1).str[0]
df["ctry"]=df.node.str[4:6]
cons=df[df["dir"]=="from_node"]
print("=== CH4 CONSUMED by technology (TWh) ===")
p=cons.groupby(["tech","year"])["val"].sum().unstack().fillna(0)/1000
print(p[p.sum(axis=1)>0.5].round(1).sort_values(2050,ascending=False).to_string())
print()
print("=== by country (TWh) ===")
print((cons.groupby(["ctry","year"])["val"].sum().unstack()/1000).round(1).to_string())
