from spinedb_api import DatabaseMapping
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
with DatabaseMapping("sqlite:///"+db) as m:
    for pv in sorted(m.get_parameter_value_items(entity_class_name="investment_group"),key=lambda x:x["entity_byname"][0]):
        n=pv["entity_byname"][0]
        if "wind-off" in n or "NS" in n:
            print(f"  {n:26} {pv['parameter_definition_name']:34} {pv['parsed_value']}")
