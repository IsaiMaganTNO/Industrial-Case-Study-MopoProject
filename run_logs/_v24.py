from spinedb_api import DatabaseMapping
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
with DatabaseMapping("sqlite:///"+db) as m:
    seen={}
    for pv in m.get_parameter_value_items(entity_class_name="unit"):
        n=pv["entity_byname"][0]
        if "wind-off" in n and "existing" not in n:
            seen.setdefault(pv["parameter_definition_name"],set()).add(n)
    for p,s in sorted(seen.items()): print(f"{p:42} {len(s)}")
    print("\n-- non-unit classes mentioning offshore --")
    for ec in m.get_entity_class_items():
        for e in m.get_entity_items(entity_class_name=ec["name"]):
            if "NSBE01" in e["name"] and ec["name"]!="unit":
                print(" ",ec["name"],e["name"]); break
