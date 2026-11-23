import os,re
from spinedb_api import DatabaseMapping, from_database
for p in [r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite",r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"]:
    print("=====",p)
    with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
        for v in db.get_parameter_value_items():
            en="|".join(v["entity_byname"])
            if "LNG-terminal" not in en: continue
            val=from_database(v["value"],v["type"]); s=str(getattr(val,"values",val))[:90]
            print(v["entity_class_name"][:22],en[:55],v["parameter_definition_name"],v["alternative_name"],s)
