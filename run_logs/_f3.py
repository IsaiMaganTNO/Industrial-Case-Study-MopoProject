import sqlite3, pandas as pd
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
cid=c.execute("select id from entity_class where name='unit_flow'").fetchone()[0]
print("unit_flow class id",cid)
print("dims:",c.execute("""select ec.name,d.position from entity_class_dimension d
  join entity_class ec on ec.id=d.dimension_id where d.entity_class_id=? order by d.position""",(cid,)).fetchall())
print("sample unit_flow entities:")
for r in c.execute("select id,name from entity where class_id=? and (name like '%atmosphere%' or name like 'oil-eng%') limit 8",(cid,)):
    print("  ",r)
print()
# the superclass trick: is unit_flow a superclass of unit__to_node?
print("superclass_subclass:", c.execute("select * from superclass_subclass").fetchall()[:10])
