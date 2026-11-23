import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
nodes=[n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"node\" order by e.name")]
import re
g=[n for n in nodes if re.search(r"ch4|methan|gas|ng_|natgas|fossil",n,re.I)]
print("gas-ish nodes:",len(g))
for n in g: print("  ",n)
