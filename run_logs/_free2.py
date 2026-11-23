import sys, collections; sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
for n in ["nb_v2","mr_fix"]:
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; w=PP.load_weights(inp)
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    for x in db.get_parameter_value_items(parameter_definition_name="units_invested_available"):
      if x["entity_byname"][1]=="DAC_NLC1": print(n,"DAC_NLC1 invested_available",[round(float(v),3) for v in x["parsed_value"].values])
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      if x["entity_byname"][1]=="DAC_NLC1" and x["entity_byname"][3]=="to_node":
        v=x["parsed_value"].values; print("  hourly CO2 out: max",round(float(max(v)),3),"mean",round(float(sum(v)/len(v)),3),"n",len(v))
