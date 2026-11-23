import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
print("entity_class names containing retro/upgrade/convert/replace:")
for (n,) in c.execute("SELECT name FROM entity_class"):
    if any(k in n.lower() for k in ("retro","upgrad","convert","replac","transform")): print("   ",n)
print("\nparameter_definition names same:")
for (n,) in c.execute("SELECT name FROM parameter_definition"):
    if any(k in n.lower() for k in ("retro","upgrad","convert","replac","transform")): print("   ",n)
print("\nentity names containing retrofit:")
n=c.execute("SELECT COUNT(*) FROM entity WHERE lower(name) LIKE '%retro%'").fetchone()[0]
print("   count:",n)
