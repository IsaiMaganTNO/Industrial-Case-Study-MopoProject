from spinedb_api import DatabaseMapping
import collections
p=r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite"
with DatabaseMapping("sqlite:///"+p) as db:
  dem=collections.defaultdict(list)
  for v in db.get_parameter_value_items(entity_class_name="node", parameter_definition_name="demand"):
    n=v["entity_name"]; pv=v["parsed_value"]
    try: val=float(pv)
    except: val=float(sum(pv.values))/len(pv.values) if hasattr(pv,"values") else str(pv)[:40]
    dem[n.split("_")[0]].append((n,v["alternative_name"],val))
  for k,l in dem.items(): print(k,len(l),l[:2])
  for v in db.get_parameter_value_items(entity_class_name="unit"):
    if v["entity_name"].startswith("LH2-terminal_NLC1") or v["entity_name"].startswith("PEM_NLC1"): print(v["entity_name"],v["parameter_definition_name"],str(v["parsed_value"])[:70])
  for v in db.get_parameter_value_items(entity_class_name="node"):
    if v["entity_name"] in ("global-H2","fossil-CH4","crude","bio_NLC1","bio_BEC1"): print(v["entity_name"],v["parameter_definition_name"],str(v["parsed_value"])[:90])
