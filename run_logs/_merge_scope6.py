import sqlite3
db=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
for c in ['unit__to_node','unit_flow__unit_flow','connection__node__node','node__temporal_block']:
  print(db.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name=? and e.name like '%BEC1%' limit 2",(c,)).fetchall())
print(db.execute("select sql from sqlite_master where name in ('entity','entity_element')").fetchall())
