import os
from spinedb_api import DatabaseMapping, from_database
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    print("ALTERNATIVES:",[a["name"] for a in db.get_alternative_items()])
    for s in db.get_scenario_items():
        sa=sorted(db.get_scenario_alternative_items(scenario_name=s["name"]),key=lambda x:x["rank"])
        print("SCENARIO",s["name"],[x["alternative_name"] for x in sa])
    seen=set()
    for v in db.get_parameter_value_items():
        a=v["alternative_name"]
        if "CO2" in a or "co2" in a.lower():
            k=(v["entity_class_name"],v["parameter_definition_name"],a); 
            if k in seen: continue
            seen.add(k); val=from_database(v["value"],v["type"])
            print(k,"|".join(v["entity_byname"])[:40],str(getattr(val,"values",val))[:80])
