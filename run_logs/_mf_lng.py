import sys,os,re
from spinedb_api import DatabaseMapping, from_database
dbs={"mr":r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite","nb":r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"}
for k,p in dbs.items():
    print("=====",k)
    with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
        for v in db.get_parameter_value_items():
            en="|".join(v["entity_byname"])
            if not re.search(r"LNG|lng",en): continue
            if not re.search(r"(NL|BE)",en): continue
            val=from_database(v["value"],v["type"])
            s=str(val); s=s if len(s)<120 else s[:120]
            print(v["entity_class_name"],en,v["parameter_definition_name"],v["alternative_name"],s)
