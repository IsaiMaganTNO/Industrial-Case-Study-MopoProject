import os,re,sys,collections
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
for run in ["nb_v2","nb_ctry"]:
  w=PP.load_weights(rf"runs\3day_{run}\input\Final_SpineOpt_Model.tiny.3day.{run}.sqlite"); c=collections.Counter()
  with DatabaseMapping("sqlite:///"+os.path.abspath(rf"runs\3day_{run}\output\Investment_Results.3day_{run}.sqlite")) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      u,n,d=v["entity_byname"][1:4]
      if d!="from_node" or not re.match(r"^H2_(BE|NL)",n): continue
      k=re.sub(r"_(BE|NL)C\d+.*$","",u)
      for y,x in PP.unpack_flow(v,w):
        if int(y)==2050: c[k]+=x/1e3
  print(run, {k:round(v,1) for k,v in c.most_common(8)})
