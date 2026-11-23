import sys, os
sys.path.insert(0,"tools")
from postprocess import load_weights
from spinedb_api import DatabaseMapping, from_database
import pandas as pd, collections
wmap=load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("wmap days:",len(wmap))
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_co2bidir.sqlite")
rows=[]
with DatabaseMapping(url) as db:
    ents={e["id"]:e for e in db.get_entity_items()}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"]!="report__connection__node__direction__stochastic_scenario": continue
        if v["parameter_definition_name"]!="connection_flow": continue
        e=ents.get(v["entity_id"]); bn=e["entity_byname"] if e else ()
        if len(bn)<4: continue
        conn,node,direc=bn[1],bn[2],bn[3]
        if not node.startswith("CH4"): continue
        val=from_database(v["value"],v["type"])
        for idx,x in zip(getattr(val,"indexes",[]),getattr(val,"values",[])):
            ts=pd.Timestamp(str(idx)); w=wmap.get(ts.strftime("%Y-%m-%d"))
            if w is None: continue
            try: xv=float(getattr(x,"value",x))
            except Exception: continue
            rows.append((conn,node,direc,ts.year,xv*w))
df=pd.DataFrame(rows,columns=["conn","node","dir","year","val"])
df.to_pickle(r"run_logs\ch4flows.pkl")
print(df.shape)
print(df.groupby("year")["val"].sum())
