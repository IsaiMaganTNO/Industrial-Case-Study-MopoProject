import sqlite3
db=r"checkpoints\Investment_Results.3day_routeemis.sqlite"
c=sqlite3.connect(db)
ns=[n for (n,) in c.execute("SELECT name FROM entity_class")]
print("slack/penalty-ish classes:",[x for x in ns if "slack" in x or "penalt" in x][:12])
