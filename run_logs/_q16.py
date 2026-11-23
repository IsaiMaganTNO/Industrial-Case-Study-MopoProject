import sqlite3
db=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
q=lambda s: db.execute(s).fetchall()
print("MeOH_NLC1 consumers:",[r[0] for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name in ('node__to_unit','connection__from_node') and e.name like 'MeOH\\_NLC1\\_\\_%' escape '\\'")])
print("methanation units:",len(q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit' and e.name like 'methanation%'")))
print("methanation atm rows:",q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit__to_node' and e.name like 'methanation%atmosphere'"))
print("bio-diges units:",q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit' and e.name like 'bio-diges%NLC1'"))
