import os,sys,re,collections
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping, from_database
res=r"runs\3day_nb_v2\output\Investment_Results.3day_nb_v2.sqlite"
ts={}
with DatabaseMapping("sqlite:///"+os.path.abspath(res)) as db:
  for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario",parameter_definition_name="connection_flow"):
    bn=v["entity_byname"]
    if "salt-cavern_NLC6" in bn[1] and bn[3]=="to_node":
      val=from_database(v["value"],v["type"])
      ts[bn[1]]=val
  for v in db.get_parameter_value_items(entity_class_name="report__node__stochastic_scenario"):
    if v["entity_byname"][1]=="salt-cavern_NLC6": ts["state:"+v["parameter_definition_name"]]=from_database(v["value"],v["type"])
for k,v in ts.items():
  def flat(x):
    while hasattr(x,"values") and len(x.values) and hasattr(x.values[0],"values"): x=x.values[-1]
    return x
  f=flat(v); vals=list(getattr(f,"values",[]))
  print(k,type(v).__name__,len(vals),[round(float(z),1) for z in vals[:72:6]])
