import sqlite3,re
c=sqlite3.connect(r"file:.spinetoolbox/items/biomass_db/biomass_db.sqlite?mode=ro",uri=True)
print([r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print(c.execute("PRAGMA table_info(entity)").fetchall())
