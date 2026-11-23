from spinedb_api import DatabaseMapping
from collections import defaultdict
SC=["Base","wy2009","medium_bio","current","GA","GA_flex0","high_CO2","flex_buildings","flex_buildings_wy2009_current","flex_industry"]
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  print("alts",[a["name"] for a in m.get_alternative_items()])
  d=defaultdict(set)
  for v in m.get_parameter_value_items(): d[(v["entity_class_name"],v["entity_byname"],v["parameter_definition_name"])].add(v["alternative_name"])
  c=defaultdict(int)
  for k,a in d.items():
    if len(a)>1: c[(k[2],tuple(sorted(a)))]+=1
  for k,n in sorted(c.items()): print(n,k)
