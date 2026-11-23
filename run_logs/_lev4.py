import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
r=c.execute("select default_value,default_type,description from parameter_definition where id=217").fetchone()
print("availability_factor(unit) default:",bytes(r[0]).decode() if r[0] else None,"type",r[1])
print("desc:",r[2])
print()
# confirm some are scalar floats not timeseries
for nm,v,t in c.execute("""select e.name,pv.value,pv.type from parameter_value pv
  join entity e on e.id=pv.entity_id where pv.parameter_definition_id=217 limit 3"""):
    print(f"  {nm:36s} type={t} {bytes(v).decode()[:60]}")
