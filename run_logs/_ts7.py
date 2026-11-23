from spinedb_api import DatabaseMapping,from_database
from collections import Counter
c=Counter();h=Counter()
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for v in m.get_parameter_value_items():
    if v["type"] not in ("time_series","map"): continue
    x=from_database(v["value"],v["type"]); idx=[str(i)[:10] for i in getattr(x,"indexes",[])]
    if len(idx)<=6 and any(i.startswith("2041-01-01") for i in idx): c[v["parameter_definition_name"]]+=1
    elif len(idx)>6 and any(i.startswith("2041") for i in idx): h[v["parameter_definition_name"]]+=1
print("YEARLY with 2041 key:",dict(c));print("HOURLY on 2041:",dict(h))
