import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("biomass cap params on bio nodes:")
for n,p,v in c.execute("""
 select e.name,pd.name,pv.value from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 where e.name like 'bio!_%' escape '!'
   and pd.name in ('node_state_max','storage_state_max','demand','max_cumulative',
                   'storage_investment_count_max_cumulative','node_type','balance_type')
 order by 1,2 limit 25"""):
    print(f"   {n:16s} {p:42s} {bytes(v).decode()[:28]}")
print()
print("count of bio_* nodes:",c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='node' and e.name like 'bio!_%' escape '!'").fetchone()[0])
print("\nALL params present on bio nodes:")
for p,k in c.execute("""select pd.name,count(*) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 where e.name like 'bio!_%' escape '!' group by 1 order by 2 desc"""):
    print(f"   {p:48s} {k}")
