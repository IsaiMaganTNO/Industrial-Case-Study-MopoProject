from spinedb_api import DatabaseMapping,from_database
from collections import Counter
c=Counter()
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for v in m.get_parameter_value_items():
    if v["type"] not in ("time_series","map"): continue
    x=from_database(v["value"],v["type"]); idx=[str(i) for i in x.indexes]
    if len(idx)<=6 and any(i.startswith("2041") for i in idx):
      c[(v["type"],type(x).__name__,v["entity_class_name"],tuple(i[:10] for i in idx),any(not isinstance(y,(int,float)) for y in x.values))]+=1
    if v["parameter_definition_name"]=="representative_blocks_by_period": print(v["entity_byname"],idx,x.values)
for k,n in c.items(): print(n,k)
