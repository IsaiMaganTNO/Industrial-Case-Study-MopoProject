from spinedb_api import DatabaseMapping
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
with DatabaseMapping("sqlite:///"+db) as m:
    for pv in m.get_parameter_value_items(entity_class_name="unit"):
        n=pv["entity_byname"][0]
        if "wind-off" in n and "existing" not in n and pv["parameter_definition_name"]=="investment_count_max_cumulative":
            print(f"  {n:38} cap={pv['parsed_value']}")
