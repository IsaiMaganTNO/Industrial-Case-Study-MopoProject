import sqlite3,re
for n in ["nb_v2","nb_ctry"]:
  d=sqlite3.connect(rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite")
  q=lambda s,*a:d.execute(s,a).fetchall()
  print("==",n)
  print(" salt-cavern ents:",q("select c.name,e.name from entity e join entity_class c on c.id=e.class_id where e.name like '%salt-cavern%' and e.name like '%NLC6%' "))
  print(" PEA ents:",[r[0] for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit' and e.name like '%PEA%' and e.name like '%NLC1%'")])
  print(" PEA to_node:",q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name in ('unit__to_node','node__to_unit') and e.name like '(H2)PEA%NLC1%'"))
