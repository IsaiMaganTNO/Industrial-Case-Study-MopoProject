import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("investment_group entities:")
for n, in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='investment_group'"):
    print("  ",n)
    eid=c.execute("select id from entity where name=?",(n,)).fetchone()[0]
    for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.entity_id=?""",(eid,)):
        print(f"      {p:46s} {bytes(v).decode()[:50]}")
print("\nbio supply/extraction units (unit__to_node into bio_*):")
for u, in c.execute("""select distinct e2.name from entity e
  join entity_class ec on ec.id=e.class_id
  join entity_element l0 on l0.entity_id=e.id and l0.position=0
  join entity e2 on e2.id=l0.element_id
  join entity_element l1 on l1.entity_id=e.id and l1.position=1
  join entity nd on nd.id=l1.element_id
  where ec.name='unit__to_node' and nd.name like 'bio!_%' escape '!' limit 12"""):
    print("  ",u)
