from spinedb_api import DatabaseMapping
import collections
for n in ["nb_v2","mr_fix","mr_ccslow"]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite") as db:
    v=[x for x in db.get_parameter_value_items(entity_class_name="unit", parameter_definition_name="investment_count_fix_new") if x["entity_name"]=="DAC_NLC1"][0]["parsed_value"]
    print(n,"fix_new",list(zip([str(i) for i in v.indexes],v.values)))
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    cls=collections.Counter()
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      if x["entity_byname"][1].startswith("DAC_"): cls[x["entity_byname"][2]]+=1
    print("  DAC unit_flow series by node:",dict(list(cls.items())[:6]))
    for pn in ["units_invested_available","units_available"]:
      xs=[x for x in db.get_parameter_value_items(parameter_definition_name=pn) if any(str(b).startswith("DAC_NLC1") for b in x["entity_byname"])]
      for x in xs[:1]: print("  ",pn,[round(float(a),3) for a in x["parsed_value"].values][:6])
