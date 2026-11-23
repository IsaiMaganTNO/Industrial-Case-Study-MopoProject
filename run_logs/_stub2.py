import re
from collections import Counter
from spinedb_api import DatabaseMapping,from_database
def info(p):
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    out={}
    for n in ["elec_DE","CH4_DE","H2_DE","CO2_DE","elec_NO","CH4_NO","elec_FR"]:
      vs={v["parameter_definition_name"]:str(from_database(v["value"],v["type"]))[:40] for v in m.get_parameter_value_items(entity_class_name="node",entity_name=n)}
      out[n]=vs
    conns=Counter()
    for e in m.get_entity_items(entity_class_name="connection"):
      mm=re.search(r"_(DE|DK|NO|UK|FR|LU)$|^(DE|DK|NO|UK|FR|LU)_",e["name"])
      if mm and re.search(r"(BE|NL)C\d",e["name"]): conns[mm.group(1) or mm.group(2)]+=1
    return out,conns
for p in [r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite",r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"]:
  o,c=info(p);print("==",p.split("\\")[-1]);print(" BE/NL<->neighbour connections",dict(c))
  for k,v in o.items(): print("  ",k,v)
