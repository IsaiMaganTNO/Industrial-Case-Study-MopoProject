import sqlite3, pandas as pd
pd.set_option("display.width",95)
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
print("tables:", [r[0] for r in c.execute("select name from sqlite_master where type='table' order by 1")])
print()
print("entity_class_dimension cols:", [r[1] for r in c.execute("PRAGMA table_info(entity_class_dimension)")])
for cls in ("unit__to_node","unit_flow__unit_flow","node__to_unit"):
    cid=c.execute("select id from entity_class where name=?",(cls,)).fetchone()[0]
    dims=c.execute("""select ec.name, d.position from entity_class_dimension d
      join entity_class ec on ec.id=d.dimension_id where d.entity_class_id=? order by d.position""",(cid,)).fetchall()
    print(cls,"id",cid,"dims",dims)
