import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
s=new["supply"]; m=s[s.carrier=="methane"]
print("=== where did the 279.1 TWh of gas GO in 2050? ===")
import sqlite3
# use the ch4 unit-flow approach on the new results
import sys, os
sys.path.insert(0,"tools")
from postprocess import load_weights
from spinedb_api import DatabaseMapping, from_database
wmap=load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_gascap.sqlite")
rows=[]
with DatabaseMapping(url) as db:
    ents={e["id"]:e for e in db.get_entity_items()}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"]!="report__unit__node__direction__stochastic_scenario": continue
        if v["parameter_definition_name"]!="unit_flow": continue
        e=ents.get(v["entity_id"]); bn=e["entity_byname"] if e else ()
        if len(bn)<4 or not bn[2].startswith("CH4_") or bn[3]!="from_node": continue
        val=from_database(v["value"],v["type"])
        for idx,x in zip(getattr(val,"indexes",[]),getattr(val,"values",[])):
            ts=pd.Timestamp(str(idx)); w=wmap.get(ts.strftime("%Y-%m-%d"))
            if w is None: continue
            try: xv=float(getattr(x,"value",x))
            except Exception: continue
            rows.append((bn[1].rsplit("_",1)[0],ts.year,xv*w))
df=pd.DataFrame(rows,columns=["tech","year","val"])
p=df.groupby(["tech","year"])["val"].sum().unstack().fillna(0)/1000
print(p[p.sum(axis=1)>0.5].round(1).sort_values(2050,ascending=False).to_string())
