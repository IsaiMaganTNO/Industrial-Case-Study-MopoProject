import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
T="BEC3_CO2_BEC6"
print("=== entities referencing",T)
for eid,cls,nm in c.execute("""
 select e.id, ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id
 where e.name like ? or e.name like ? """,(f"%{T}%",f"%{T}%")):
    print(f"  id={eid:6d} class={cls:32s} name={nm}")
print("\n=== multi-dim entities having T as an element")
for eid,cls,nm in c.execute("""
 select distinct e.id, ec.name, e.name from entity e
 join entity_class ec on ec.id=e.class_id
 join entity_element el on el.entity_id=e.id
 join entity t on t.id=el.element_id
 where t.name=? """,(T,)):
    print(f"  id={eid:6d} class={cls:32s} name={nm}")
    for pd_,alt,val in c.execute("""
      select pd.name, a.name, pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join alternative a on a.id=pv.alternative_id where pv.entity_id=?""",(eid,)):
        print(f"        {pd_:40s} [{alt}] = {val[:40]}")
print("\n=== params directly on the connection entity")
for eid, in c.execute("select id from entity where name=?",(T,)):
    for pd_,alt,val in c.execute("""
      select pd.name, a.name, pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join alternative a on a.id=pv.alternative_id where pv.entity_id=?""",(eid,)):
        print(f"   {pd_:40s} [{alt}] = {val[:40]}")
