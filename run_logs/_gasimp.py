import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# connections touching CH4 nodes
rows=[n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"connection\" and e.name like \"%CH4%\"")]
print("CH4 connections:",len(rows))
for r in rows[:60]: print("  ",r)
print()
# which involve foreign nodes
f=[r for r in rows if any(x in r for x in ["_DE","_FR","_UK","_LU"])]
print("involving foreign CH4 nodes:",len(f))
for r in f: print("  ",r)
