import sqlite3
# what the current (IC1-only) vre_db calls its non-IC1 regions
c = sqlite3.connect("file:.spinetoolbox/items/vre_db/vre_db.sqlite?mode=ro", uri=True)
names = sorted(x[0] for x in c.execute(
    """SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
       WHERE ec.name='region'""").fetchall())
c.close()
other = [n for n in names if not n.startswith(("BEC","NLC"))]
print("vre_db non-IC1 regions (%d):" % len(other))
print(" ", other[:40])
print()
# transmission_db country stubs
c = sqlite3.connect("file:.spinetoolbox/items/transmission_db/transmission_db.sqlite?mode=ro", uri=True)
t = sorted(x[0] for x in c.execute(
    """SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
       WHERE ec.name='region'""").fetchall())
c.close()
print("transmission_db regions (%d):" % len(t))
print(" ", t)
