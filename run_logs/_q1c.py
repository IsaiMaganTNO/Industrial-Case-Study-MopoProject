from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite"
U=["methanation_NLC1","gas-boiler_NLC1","LH2-terminal_NLC1","(H2)MeOH-DC_NLC1","(COEL)MeOH-MEA_NLC1","REF-SMR-MEA_NLC1","LNG-terminal_NLC1","bio-boiler_NLC1","(BM)NH3_NLC1","MOE_NLC1","(NG)DRI-EAF-MEA_NLC1"]
with DatabaseMapping("sqlite:///"+p) as db:
  for c in ("node__to_unit","unit__to_node"):
    for e in db.get_entity_items(entity_class_name=c):
      b=e["entity_byname"]
      if any(u in b for u in U): print(c,b)
  for c in ("unit_flow__unit_flow",):
    for v in db.get_parameter_value_items(entity_class_name=c):
      b=v["entity_byname"]
      if any(u in b for u in U): print(v["parameter_definition_name"],b,v["parsed_value"] if not hasattr(v["parsed_value"],"values") else list(v["parsed_value"].values)[:3])
