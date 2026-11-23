import os,re,sys,pickle,collections,pandas as pd
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
R={"SA":"nb_v2","CL":"nb_ctry"}
NET=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_((BE|NL)(C\d+)?)$")
out={}
for k,n in R.items():
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; res=rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite"
  w=PP.load_weights(inp); rows=[]
  with DatabaseMapping("sqlite:///"+os.path.abspath(res)) as db:
    for cls,par in [("report__unit__node__direction__stochastic_scenario","unit_flow"),("report__connection__node__direction__stochastic_scenario","connection_flow")]:
      for v in db.get_parameter_value_items(entity_class_name=cls,parameter_definition_name=par):
        bn=v["entity_byname"]; obj,node,d=bn[1],bn[2],bn[3]
        m=NET.match(node)
        if not m: continue
        for y,x in PP.unpack_flow(v,w):
          rows.append((m.group(1),m.group(3),obj,"unit" if "unit" in cls else "conn",d,int(y),x))
  out[k]=pd.DataFrame(rows,columns=["car","ctry","obj","kind","dir","year","v"])
  print(k,len(rows))
pickle.dump(out,open(r"run_logs\_bal_sa_cl.pkl","wb"))
