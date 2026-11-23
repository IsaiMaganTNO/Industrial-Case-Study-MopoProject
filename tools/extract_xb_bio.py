import os,re,sys,collections,pandas as pd
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
run,inp,out,dst=sys.argv[1:5]
w=PP.load_weights(inp); rows=[]; bio=[]
with DatabaseMapping("sqlite:///"+os.path.abspath(out)) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
        conn,node,d=v["entity_byname"][1:4]
        m=re.match(r"^([A-Z]{2}\w*?)_(CH4|H2|elec|CO2)_([A-Z]{2}\w*)$",conn)
        if not m or d!="to_node": continue
        a,car,b=m.groups()
        if a[:2]==b[:2]: continue
        # compare COUNTRY codes: country-level nodes are CH4_BE / CH4_NL while the
        # connection keeps zone names (FR_CH4_BEC3) -> node.endswith(b) mis-assigned direction
        nc=node.rsplit("_",1)[-1][:2]
        dest=b if nc==b[:2] else a; orig=a if dest==b else b
        for y,x in PP.unpack_flow(v,w): rows.append((car,orig[:2],dest[:2],int(y),x))
    for v in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
        u,n,d=v["entity_byname"][1:4]
        if d!="from_node" or not re.match(r"^bio",n,re.I): continue
        m=re.search(r"_((BE|NL)C\d|BE|NL|DE|DK|NO|UK|FR|LU)$",n)
        for y,x in PP.unpack_flow(v,w): bio.append((n,u,(m.group(1)[:2] if m else "?"),int(y),x))
pd.to_pickle({"xb":pd.DataFrame(rows,columns=["car","o","d","year","v"]),"bio":pd.DataFrame(bio,columns=["node","unit","c","year","v"])},dst)
print(run,len(rows),len(bio))

