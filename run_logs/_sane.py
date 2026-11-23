import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# 1. no duplicate entity names within a class
d=c.execute("select class_id,name,count(*) n from entity group by 1,2 having n>1").fetchall()
print("duplicate (class,name):",len(d))
# 2. every new connection has exactly 1 from, 1 to, 1 node__node
bad=c.execute("""
 select e.name,
   (select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
      where x.class_id=16 and el.element_id=e.id),
   (select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
      where x.class_id=20 and el.element_id=e.id),
   (select count(*) from entity x join entity_element el on el.entity_id=x.id and el.position=0
      where x.class_id=53 and el.element_id=e.id)
 from entity e where e.class_id=1 and e.name like '%!_CO2!_%' escape '!'""").fetchall()
off=[r for r in bad if r[1:]!=(1,1,1)]
print("CO2 conns with wrong from/to/nnn counts:",len(off),off[:3])
print("total CO2 conns checked:",len(bad))
# 3. node__node orientation must be (out=to_node, in=from_node) - matches forward convention
mis=0
for nm, in c.execute("select name from entity where class_id=1 and name like '%!_CO2!_%' escape '!'"):
    a,_,b=nm.partition("_CO2_")
    nn=c.execute("""select e2.name,e3.name from entity e
      join entity_element l1 on l1.entity_id=e.id and l1.position=1
      join entity e2 on e2.id=l1.element_id
      join entity_element l2 on l2.entity_id=e.id and l2.position=2
      join entity e3 on e3.id=l2.element_id
      join entity_element l0 on l0.entity_id=e.id and l0.position=0
      join entity c0 on c0.id=l0.element_id
      where e.class_id=53 and c0.name=?""",(nm,)).fetchone()
    if nn!=(f"CO2_{b}",f"CO2_{a}"): mis+=1
print("node__node orientation mismatches:",mis)
# 4. parameter_type / value_list sanity on our new params
print("\nnew param rows with NULL type (matches forward?):")
print(c.execute("""select pv.type,count(*) from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  where pd.name in ('connection_flow_cost','fix_ratio_out_in_connection_flow') group by 1""").fetchall())
