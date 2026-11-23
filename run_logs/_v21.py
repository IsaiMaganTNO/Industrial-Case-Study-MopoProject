from spinedb_api import DatabaseMapping
import numpy as np
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
tgt=[f"nuclear-3_{c}{i}" for c,n in [("BEC",8),("NLC",9)] for i in range(1,n+1)]
with DatabaseMapping("sqlite:///"+db) as m:
    for p in ["investment_count_fix_new","unit_investment_cost","investment_count_max_cumulative"]:
        print("=====",p)
        for pv in sorted(m.get_parameter_value_items(entity_class_name="unit"),key=lambda x:x["entity_byname"][0]):
            n=pv["entity_byname"][0]
            if n in tgt and pv["parameter_definition_name"]==p:
                v=pv["parsed_value"]
                try:
                    s=dict(zip([str(i)[:10] for i in v.indexes],[round(float(x),4) for x in v.values]))
                except Exception:
                    s=v
                print(f"  {n:18} {s}")
