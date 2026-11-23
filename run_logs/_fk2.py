import sqlite3
base=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
new =r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite"
for tag,db in [("BASELINE",base),("PATCHED ",new)]:
    c=sqlite3.connect(db)
    v=c.execute("pragma foreign_key_check").fetchall()
    print(f"{tag}: foreign_key_check violations = {len(v)}")
c=sqlite3.connect(new)
v=c.execute("pragma foreign_key_check").fetchall()
# what rows? rowid -> inspect
import collections
by=collections.Counter((r[0],r[2],r[3]) for r in v)
print("\nviolation groups (table, parent, fkid):",by)
rid=v[0][1]
print("\nsample offending entity_element row:",
      c.execute("select rowid,* from entity_element where rowid=?",(rid,)).fetchall())
print("fk list for entity_element:",c.execute("pragma foreign_key_list(entity_element)").fetchall())
