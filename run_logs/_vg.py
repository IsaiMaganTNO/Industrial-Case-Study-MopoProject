import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
rows=list(c.execute("""select e.name,pv.value,pv.type,al.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  join alternative al on al.id=pv.alternative_id
  where pd.name='investment_count_total_max_cumulative' and ec.name='investment_group'
  and (e.name like 'wind-on%' or e.name like 'solar-PV%') order by e.name"""))
print(f"rows: {len(rows)}")
for n,v,t,a in rows:
    print(f"  {n:24s} type={t:6s} alt={a:6s} {bytes(v).decode()}")
