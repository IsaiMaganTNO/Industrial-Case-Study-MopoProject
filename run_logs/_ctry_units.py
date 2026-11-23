import sqlite3
c=sqlite3.connect(r"runs\3day_nb_ctry_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ctry_ccslow.sqlite")
print([n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and (e.name like 'methanation%' or e.name like 'DAC%')")])
