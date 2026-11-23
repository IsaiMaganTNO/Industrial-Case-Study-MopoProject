import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("=== ALL params on node fossil-CH4, both alternatives ===")
for p,v,a in c.execute("""select pd.name,pv.value,al.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id
  where e.name='fossil-CH4' order by al.name,pd.name"""):
    print(f"  [{a:19s}] {p:34s} {bytes(v).decode()[:150]}")
print()
print("=== does ANY unit in the model use availability_factor? (precedent check) ===")
n=c.execute("""select count(*) from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='availability_factor' and ec.name='unit'""").fetchone()[0]
print("   unit-level availability_factor rows:",n)
for nm,a in c.execute("""select e.name,al.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  join alternative al on al.id=pv.alternative_id
  where pd.name='availability_factor' and ec.name='unit' and e.name not like 'solar%' and e.name not like 'wind%' limit 12"""):
    print(f"      {nm:44s} [{a}]")
