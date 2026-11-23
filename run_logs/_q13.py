import sqlite3,collections
db=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
q=lambda s: db.execute(s).fetchall()
# who consumes HC_NLC1 / CH4_NLC1 (units + connections)
for nd in ["HC_NLC1","CH4_NLC1"]:
  u=[n for (n,) in q(f"select e.name from entity e join entity_class c on c.id=e.class_id where c.name='node__to_unit' and e.name like '{nd}\\_\\_%' escape '\\'")]
  cn=[n for (n,) in q(f"select e.name from entity e join entity_class c on c.id=e.class_id where c.name='connection__from_node' and e.name like '%{nd}'")]
  print(nd,"units:",len(u),[x.split("__")[1] for x in u][:30]); print("  conns:",cn[:10])
