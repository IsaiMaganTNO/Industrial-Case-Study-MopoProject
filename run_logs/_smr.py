import sqlite3
d=sqlite3.connect(r"runs\3day_nb_ctry\input\Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite")
print(d.execute("select c.name,e.name from entity e join entity_class c on c.id=e.class_id where c.name in ('unit__to_node','node__to_unit') and e.name like 'REF-SMR%NLC1%'").fetchall())
