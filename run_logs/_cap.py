import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for u in ["solar-PV-no-tracking_NLC1","wind-on-SP277-HH100_NLC1","solar-PV-existing_NLC1"]:
    r=c.execute("""select pd.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=?
      and pd.name in ('unit_capacity','investment_count_max_cumulative','investment_count_initial_cumulative')""",(u,)).fetchall()
    print(u)
    for p,v in r: print(f"     {p:42s} {bytes(v).decode()[:40]}")
# capacity on unit__to_node
print("\nunit__to_node capacity for solar/wind (GW per unit):")
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  where pd.name='unit_capacity' and (e.name like 'solar-PV%NLC1%' or e.name like 'wind-on%NLC1%') limit 6"""):
    print(f"   {n:46s} {bytes(v).decode()[:24]}")
