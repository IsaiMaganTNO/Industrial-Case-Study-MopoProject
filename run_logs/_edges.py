import sqlite3
b=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite")
old={r[0] for r in b.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection'")}
# edges used in the two cheapest BE routes
used=["BEC7_CO2_BEC2","BEC2_CO2_BEC1","BEC1_CO2_NLC6","BEC6_CO2_BEC5","BEC5_CO2_NLC6"]
print("edges on the cheapest Belgian routes to storage:")
for e in used:
    print(f"   {e:18s} existed_before={e in old}")
print()
# injection cost context
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for u,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='vom_cost' and e.name like 'CO2-injection%' order by 1"""):
    print(f"   injector {u:34s} vom_cost={float(bytes(v).decode()):.4f}")
