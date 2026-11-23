from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite"
with DatabaseMapping("sqlite:///"+p) as db:
  print([c["name"] for c in db.get_entity_class_items() if "unit" in c["name"]])
  for c in [c["name"] for c in db.get_entity_class_items() if c["name"].startswith(("unit__","node__unit"))]:
    xs=[e["entity_byname"] for e in db.get_entity_items(entity_class_name=c) if "methanation_NLC1" in e["entity_byname"] or "gas-boiler_NLC1" in e["entity_byname"] or "LH2-terminal_NLC1" in e["entity_byname"] or "(H2)MeOH-DC_NLC1" in e["entity_byname"]]
    if xs: print(c, xs)
