from spinedb_api import DatabaseMapping
for n in ["nb_v2","mr_fix"]:
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite") as db:
    units={e["name"] for e in db.get_entity_items(entity_class_name="unit")}
    ex={x["entity_name"] for x in db.get_parameter_value_items(entity_class_name="unit",parameter_definition_name="existing_units")}
    miss=sorted(units-ex)
    import collections; c=collections.Counter(m.split("_")[0] for m in miss)
    print(n,"units",len(units),"with explicit existing_units",len(ex),"relying on default 1.0:",len(miss)); print("  ",c.most_common(25))
