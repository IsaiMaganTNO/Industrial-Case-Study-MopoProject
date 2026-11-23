from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping(r"sqlite:///checkpoints/Investment_Results.3day_nodac_nuc.sqlite") as m:
  for v in m.get_parameter_value_items():
    e="__".join(v["entity_byname"])
    if ("NSNL" in e and "storage" in e or e.startswith("atmosphere")) and v["parameter_definition_name"] in ("storages_invested_available","node_state_longterm","storages_invested"):
      x=from_database(v["value"],v["type"])
      print(e,v["parameter_definition_name"]); 
      for i,y in zip(x.indexes,x.values): print("  ",str(i)[:19],round(float(y),4))
