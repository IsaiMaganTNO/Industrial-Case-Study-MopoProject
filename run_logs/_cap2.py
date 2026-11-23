import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("params on unit__to_node for solar-PV-no-tracking_NLC1:")
for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  join entity_element l0 on l0.entity_id=e.id and l0.position=0
  join entity u on u.id=l0.element_id
  join entity_class ec on ec.id=e.class_id
  where ec.name='unit__to_node' and u.name='solar-PV-no-tracking_NLC1'"""):
    print(f"   {p:44s} {bytes(v).decode()[:48]}")
print("\nsame for wind-on-SP277-HH100_NLC1:")
for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  join entity_element l0 on l0.entity_id=e.id and l0.position=0
  join entity u on u.id=l0.element_id
  join entity_class ec on ec.id=e.class_id
  where ec.name='unit__to_node' and u.name='wind-on-SP277-HH100_NLC1'"""):
    print(f"   {p:44s} {bytes(v).decode()[:48]}")
