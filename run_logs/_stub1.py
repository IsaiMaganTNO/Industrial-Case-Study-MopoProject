import re
from collections import Counter
from spinedb_api import DatabaseMapping,from_database
P=r"sqlite:///runs/3day_nn_fix/input/Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite"
IN=re.compile(r"(BE|NL)C\d|^NS(NL|BE)")
with DatabaseMapping(P) as m:
  nodes={e["name"] for e in m.get_entity_items(entity_class_name="node")}
  ext=sorted(n for n in nodes if not IN.search(n))
  print("non-NL/BE nodes",len(ext)); print(ext[:60])
  cn=[e for e in m.get_entity_items(entity_class_name="connection__from_node")]
  touch=Counter()
  for e in cn:
    a,b=e["entity_byname"]
    if not IN.search(b): touch[re.sub(r"\d","",b.split("_")[-1]) if "_" in b else b]+=1
  print("conn from external nodes",dict(touch.most_common(20)))
  for n in ext[:8]:
    vs=[(v["parameter_definition_name"],v["alternative_name"]) for v in m.get_parameter_value_items(entity_class_name="node",entity_name=n)]
    print(n,vs[:6])
