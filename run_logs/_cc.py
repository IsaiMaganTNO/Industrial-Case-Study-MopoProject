import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
print([r[1] for r in c.execute("pragma table_info(entity_class)")])
for r in c.execute("select id,name from entity_class where name like '%connection%'"):
    print(r)
