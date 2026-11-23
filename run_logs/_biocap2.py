import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("entities with 'bio' in name, by class:")
for cls,n in c.execute("""select ec.name,count(*) from entity e join entity_class ec on ec.id=e.class_id
  where lower(e.name) like '%bio%' group by 1 order by 2 desc limit 12"""):
    print(f"   {cls:28s} {n}")
print("\nbio-related nodes with storage caps (the biocap365 patch target):")
for n,p,v in c.execute("""select e.name,pd.name,pv.value from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 where lower(e.name) like '%bio%'
   and pd.name like '%max%' order by 1 limit 20"""):
    print(f"   {n:26s} {p:44s} {bytes(v).decode()[:26]}")
