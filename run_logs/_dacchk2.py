from spinedb_api import DatabaseMapping, from_database
for n,f in [("mr_fix","input\\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"),("mr_ccslow","input\\Final_SpineOpt_Model.tiny.3day.mr_ccslow.sqlite")]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\{f}") as db:
    for v in db.get_parameter_value_items(entity_class_name="unit", parameter_definition_name="investment_count_fix_new"):
      if v["entity_name"] in ("DAC_NLC1","DAC_UK"): print(n,v["entity_name"],v["parsed_value"])
    for c in ("unit__from_node","unit__to_node"):
      for e in db.get_entity_items(entity_class_name=c):
        if e["entity_byname"][0]=="DAC_NLC1": print("  ",c,e["entity_byname"])
    for v in db.get_parameter_value_items(entity_class_name="unit"):
      if v["entity_name"]=="DAC_NLC1" and v["parameter_definition_name"] in ("initial_units_invested_available","units_existing","number_of_units"): print("  ",v["parameter_definition_name"],v["parsed_value"])
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    for pd_ in ("units_invested_available","units_invested","units_on"):
      for v in db.get_parameter_value_items(parameter_definition_name=pd_):
        if "DAC_NLC1" in v["entity_byname"]: print("  OUT",pd_,v["entity_byname"],str(v["parsed_value"])[:200]); break
