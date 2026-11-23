import os,re,collections,sys,pickle,pandas as pd
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
w=PP.load_weights(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
C=lambda s: s[:2]
rows=[]
with DatabaseMapping("sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mr_fix.sqlite")) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
        conn,node,d=v["entity_byname"][1:4]
        m=re.match(r"^([A-Z]{2}\w*?)_(CH4|H2|elec|CO2)_([A-Z]{2}\w*)$",conn)
        if not m or d!="to_node": continue
        a,car,b=m.groups()
        if C(a)==C(b): continue
        # to_node flow: delivered to node; determine direction via node name
        dest=b if node.endswith(b) else a; orig=a if dest==b else b
        for y,x in PP.unpack_flow(v,w): rows.append((car,C(orig),C(dest),int(y),x))
df=pd.DataFrame(rows,columns=["car","o","d","year","v"])
g=df.groupby(["car","o","d","year"]).v.sum().unstack().fillna(0)/1e3
print("units: TWh (CO2: Mt)"); print(g[(g.abs()>0.5).any(axis=1)].round(1).to_string())
df.to_pickle(r"run_logs\mr_fix_xb.pkl")
