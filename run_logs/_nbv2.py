import re
from spinedb_api import DatabaseMapping,from_database
with DatabaseMapping("sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite") as m:
  for v in m.get_parameter_value_items():
    e="__".join(v["entity_byname"]);p=v["parameter_definition_name"];a=v["alternative_name"]
    show=(e=="atmosphere" and "cumulative" in p) or (e.startswith("CO2-storage") and a=="high_CO2") or (e.startswith("nuclear-3") and v["entity_class_name"]=="investment_group") or (p=="weight") or (e.startswith("LNG-terminal_BEC1") and p=="availability_factor") or (e=="DAC_NLC2" and p=="investment_count_max_cumulative")
    if show:
      x=from_database(v["value"],v["type"]);print(e,p,a,[str(i)[:10] for i in getattr(x,"indexes",[])],[round(float(y),4) for y in getattr(x,"values",[x])] if not isinstance(x,bool) else x)
  print("scenarios",[s["name"] for s in m.get_scenario_items()])
