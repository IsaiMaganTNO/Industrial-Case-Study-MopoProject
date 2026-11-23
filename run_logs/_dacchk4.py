import sys; sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
import collections
for n in ["nb_v2","mr_fix","mr_ccslow"]:
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"
  with DatabaseMapping("sqlite:///"+inp) as db:
    caps=[(x["entity_class_name"],x["entity_byname"],x["parsed_value"]) for x in db.get_parameter_value_items(parameter_definition_name="unit_capacity") if x["entity_byname"][0]=="DAC_NLC1"]
    print(n,"unit_capacity DAC_NLC1:",caps)
  w=PP.load_weights(inp); s=collections.defaultdict(float)
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      if x["entity_byname"][1].startswith("DAC_"):
        for y,v in PP.unpack_flow(x,w): s[(int(y),x["entity_byname"][2].split("_")[0],x["entity_byname"][3])]+=v
  print("  ",{k:round(v/1e3,2) for k,v in sorted(s.items()) if abs(v)>1})
