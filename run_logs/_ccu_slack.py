import os, collections
from spinedb_api import DatabaseMapping, from_database
url="sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite")
tot=collections.Counter(); seen=set()
with DatabaseMapping(url) as db:
    for v in db.get_parameter_value_items():
        p=v["parameter_definition_name"]
        if "slack" not in p and "penal" not in p: continue
        seen.add((v["entity_class_name"],p))
        val=from_database(v["value"],v["type"])
        def walk(x,key):
            if hasattr(x,"values") and hasattr(x,"indexes"):
                for i,y in zip(x.indexes,x.values): walk(y,key+(str(i)[:4],))
            else:
                try:
                    f=float(x)
                    if abs(f)>1e-6: tot[(p,"/".join(v["entity_byname"]),key[-1] if key else "")]+=f
                except: pass
        walk(val,())
print(seen)
for k,s in sorted(tot.items(),key=lambda kv:-abs(kv[1]))[:30]: print(k, round(s,3))
