import sqlite3, os
p = ".spinetoolbox/items/commodity_db/commodity_db.sqlite"
print("exists", os.path.exists(p), "size", os.path.getsize(p))
c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
for t in ["entity", "entity_class", "parameter_value", "alternative"]:
    print(" ", t, c.execute("SELECT count(*) FROM %s" % t).fetchone()[0])
c.close()
