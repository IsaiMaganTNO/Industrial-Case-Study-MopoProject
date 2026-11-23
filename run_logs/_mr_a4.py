import sys, os, re, pickle, pandas as pd
sys.path.insert(0,"tools")
import postprocess as PP
from spinedb_api import DatabaseMapping
pd.set_option("display.width",250)
wmap=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
def ctry(n):
    m=re.search(r"_((?:BE|NL)C\d|DE|DK|NO|UK|[A-Z]{2})$", n)
    if not m: return None
    r=m.group(1); return r[:2] if len(r)>2 else r
def carrier(n):
    n=n.split("_")[0]
    return {"elec":"elec","CH4":"CH4","H2":"H2","CO2":"CO2"}.get(n, n)
rows=[]
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
with DatabaseMapping(url) as db:
    ents={e["id"]:e for e in db.get_entity_items()}
    for v in db.get_parameter_value_items():
        if v["entity_class_name"]!="report__connection__node__direction__stochastic_scenario" or v["parameter_definition_name"]!="connection_flow": continue
        bn=ents[v["entity_id"]]["entity_byname"]
        conn,node,d=bn[1],bn[2],bn[3]
        for y,x in PP.unpack_flow(v,wmap):
            if abs(x)>1e-9: rows.append((conn,node,d,y,x))
df=pd.DataFrame(rows,columns=["conn","node","dir","year","val"])
df["car"]=df.node.map(carrier); df["c"]=df.node.map(ctry)
pickle.dump(df,open(r"run_logs\mixedres_connflow.pkl","wb"))
# net imports per country = to_node inflow - from_node outflow, across connections linking different countries
to=df[df.dir=="to_node"]; fr=df[df.dir=="from_node"]
# per-connection endpoint countries
ends=df.groupby("conn").c.agg(lambda s: tuple(sorted(set(s.dropna()))))
x=df[df.conn.map(lambda c: len(ends[c])==2)]
imp=(x[x.dir=="to_node"].groupby(["car","c","year"]).val.sum() - x[x.dir=="from_node"].groupby(["car","c","year"]).val.sum()).fillna(0)
print("=== NET CROSS-BORDER IMPORT (TWh; + = import, connections between different countries)")
print((imp.unstack()/1e3).round(1).to_string())
print("\nunknown-country nodes:", sorted(df[df.c.isna()].node.unique())[:15])
