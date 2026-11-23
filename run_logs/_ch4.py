import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for T in ["BEC1_CH4_BEC2","BEC2_CH4_BEC1"]:
    print("="*60); print(T)
    for eid,cls,nm in c.execute("""
     select distinct e.id, ec.name, e.name from entity e
     join entity_class ec on ec.id=e.class_id
     left join entity_element el on el.entity_id=e.id
     left join entity t on t.id=el.element_id
     where e.name=? or t.name=?""",(T,T)):
        print(f"  {cls:26s} {nm}")
        for pd_,alt,val in c.execute("""
          select pd.name,a.name,pv.value from parameter_value pv
          join parameter_definition pd on pd.id=pv.parameter_definition_id
          join alternative a on a.id=pv.alternative_id where pv.entity_id=?""",(eid,)):
            print(f"      {pd_:38s} [{alt}] = {val[:34]}")
