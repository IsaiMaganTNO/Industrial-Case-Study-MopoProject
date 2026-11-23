import sqlite3
c=sqlite3.connect(r".spinetoolbox\items\transport_db\transport_db.sqlite")
cur=c.cursor()
print("entity count:",cur.execute("SELECT count(*) FROM entity").fetchone()[0])
print("entity_class count:",cur.execute("SELECT count(*) FROM entity_class").fetchone()[0])
print("classes:",cur.execute("SELECT id,name FROM entity_class").fetchall())
print("first 5 entities:",cur.execute("SELECT id,class_id,name FROM entity LIMIT 5").fetchall())
c.close()
