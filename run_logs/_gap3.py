import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
cls=c.execute("SELECT id FROM entity_class WHERE name='unit__to_node'").fetchone()[0]
print("unit__to_node class_id",cls)
print("dims:",c.execute("SELECT dimension_id,position FROM entity_class_dimension WHERE entity_class_id=? ORDER BY position",(cls,)).fetchall())
e=c.execute("SELECT id,name FROM entity WHERE class_id=? AND name LIKE '%__atmosphere' LIMIT 1",(cls,)).fetchone()
print("sample:",e)
print("elements:",c.execute("SELECT entity_id,entity_class_id,position,element_id,dimension_id FROM entity_element WHERE entity_id=?",(e[0],)).fetchall())
for d,_ in c.execute("SELECT dimension_id,position FROM entity_class_dimension WHERE entity_class_id=? ORDER BY position",(cls,)):
    print("dim",d,c.execute("SELECT name FROM entity_class WHERE id=?",(d,)).fetchone())
print("atmosphere node id:",c.execute("SELECT id,class_id FROM entity WHERE name='atmosphere'").fetchall())
