import os
from spinedb_api import DatabaseMapping, from_database
for p in [r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite",r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"]:
  with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    tot={}
    for v in db.get_parameter_value_items(entity_class_name="node",parameter_definition_name="storage_investment_count_fix_cumulative"):
        if not v["entity_name"].startswith("CO2-storage"): continue
        val=from_database(v["value"],v["type"]); x=list(val.values)
        tot.setdefault(v["alternative_name"],[0]*len(x))
        tot[v["alternative_name"]]=[a+b*365 for a,b in zip(tot[v["alternative_name"]],x)]
    print(p.split("\\")[1], {k:[round(a,1) for a in t] for k,t in tot.items()})
