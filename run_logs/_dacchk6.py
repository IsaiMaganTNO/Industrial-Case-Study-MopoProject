from spinedb_api import DatabaseMapping
for n in ["mr_fix","mr_ccslow"]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    m=0;c=0
    for x in db.get_parameter_value_items():
      if any(str(b).startswith("DAC_") for b in x["entity_byname"]) and x["parameter_definition_name"].startswith("units"):
        c+=1; m=max(m,max(float(v) for v in x["parsed_value"].values))
    print(n,"DAC unit-count series:",c,"max units:",m)
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite") as db:
    rel=[(x["entity_class_name"],x["parameter_definition_name"]) for x in db.get_parameter_value_items() if x["entity_class_name"].startswith("unit__") and x["entity_byname"][0]=="DAC_NLC1"]
    print("  DAC_NLC1 relationship params:",sorted(set(rel)))
