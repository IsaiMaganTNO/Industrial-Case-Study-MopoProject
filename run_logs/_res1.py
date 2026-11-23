import sqlite3
c=sqlite3.connect(r"checkpoints\Investment_Results.3day_co2bidir.sqlite")
ns=[n for (n,) in c.execute("select name from entity_class order by name")]
print("result classes:",[x for x in ns if "connection" in x or "unit" in x or "node" in x][:25])
print()
# find reports
for (n,) in c.execute("select name from entity_class order by name"):
    cnt=c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name=?",(n,)).fetchone()[0]
    if cnt: print(f"  {n:50s} {cnt}")
