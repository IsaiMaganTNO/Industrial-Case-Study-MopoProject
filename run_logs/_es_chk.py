import sqlite3
c=sqlite3.connect(r"share_frlu_xpress\input.sqlite")
for n in ("CH4_ES","H2_ES"):
  print(n,[r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where e.name like ? and ec.name not like 'node__temporal%'",(f"%{n}%",))])
