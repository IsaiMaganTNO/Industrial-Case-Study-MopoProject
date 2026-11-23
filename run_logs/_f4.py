import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
name="SCPC-existing_NLC4__atmosphere__coal__SCPC-existing_NLC4"
r=c.execute("select id,class_id,name from entity where name=?",(name,)).fetchone()
print("ff entity:",r)
for row in c.execute("""select ee.position, ee.element_id, e2.name, ec.name
  from entity_element ee join entity e2 on e2.id=ee.element_id
  join entity_class ec on ec.id=e2.class_id where ee.entity_id=? order by ee.position""",(r[0],)):
    print("  pos",row)
print()
n2="SCPC-existing_NLC4__atmosphere"
print("unit__to_node:",c.execute("select id,class_id,name from entity where name=?",(n2,)).fetchone())
n3="coal__SCPC-existing_NLC4"
print("node__to_unit:",c.execute("select id,class_id,name from entity where name=?",(n3,)).fetchone())
print()
pdid=c.execute("select id,entity_class_id from parameter_definition where name='flow_ratio_equality_coefficient'").fetchall()
print("param defs:",pdid)
print("alternatives:",c.execute("select id,name from alternative").fetchall())
