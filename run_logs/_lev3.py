import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for pid,nm,cls in c.execute("""select pd.id,pd.name,ec.name from parameter_definition pd
  join entity_class ec on ec.id=pd.entity_class_id where pd.name='availability_factor'"""):
    print("param def",pid,nm,"on class",cls)
print()
rows=list(c.execute("""select distinct e.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='availability_factor' and ec.name='unit'
  and (e.name like 'CCGT%' or e.name like '%boiler%' or e.name like 'LNG%' or e.name like 'gas-ex%')"""))
print("thermal units with availability_factor:",rows if rows else "NONE")
print()
# what DOES limit a thermal unit's output? check a CCGT
print("params on CCGT+CC_NLC3__elec_NLC3 (the to_node rel):")
for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id where e.name like 'CCGT+CC_NLC3__%'"""):
    print(f"   {p:28s} {bytes(v).decode()[:60]}")
