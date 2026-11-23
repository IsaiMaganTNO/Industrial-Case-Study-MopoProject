import sqlite3,json,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for pat in ("LNG-terminal","gas-extraction"):
    print("=== %s ==="%pat)
    for n,v in c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN entity e ON e.id=pv.entity_id JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%atmosphere%' LIMIT 3""",("%"+pat+"%",)):
        print("   ",n[:70]); print("     ",v[:90])
