from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite") as m:
  for al in ["limited_nuclear-3","limited_fossil-CH4","flex_industry"]:
    vs=m.get_parameter_value_items(alternative_name=al); print(al,len(vs))
    for v in vs[:4]:
      x=from_database(v["value"],v["type"]); print("  ",v["entity_byname"],v["parameter_definition_name"],getattr(x,"indexes",""),getattr(x,"values",x))
