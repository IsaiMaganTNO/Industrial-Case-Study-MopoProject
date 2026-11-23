import sqlite3,collections
d=sqlite3.connect(r"checkpoints/Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite")
q=lambda s,*a:d.execute(s,a).fetchall()
v=q("PRAGMA foreign_key_check"); print(len(v), collections.Counter((r[0],r[3]) for r in v))
print(q("PRAGMA foreign_key_list(entity_element)"))
rows=[r[1] for r in v[:3]]
for r in rows: print(q("select ee.*, (select name from entity where id=ee.entity_id),(select name||' cls'||class_id from entity where id=ee.element_id) from entity_element ee where rowid=?",r))
