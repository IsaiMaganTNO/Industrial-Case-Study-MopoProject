import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
for r in c.execute("select name,sql from sqlite_master where type='table' and name in ('entity','entity_element','parameter_value','entity_alternative','entity_group','entity_location')"): print(r[0]);print(r[1][:600]);print()
print(c.execute("pragma foreign_keys").fetchall())
