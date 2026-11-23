import sqlite3
c=sqlite3.connect(r".spinetoolbox\items\transport_db\transport_db.sqlite")
cur=c.cursor()
cls={r[0]:r[1] for r in cur.execute("SELECT id,name FROM entity_class")}
bad=[]
for eid,cid,nm in cur.execute("SELECT id,class_id,name FROM entity"):
    if cls[cid]!="commodity__vehicle__region": continue
    n=cur.execute("SELECT count(*) FROM entity_element WHERE entity_id=?",(eid,)).fetchone()[0]
    if n!=3: bad.append((eid,nm,n))
print("composites with wrong element count:",len(bad))
for b in bad[:6]: print("  ",b)
print("\nparameter_values attached to those:",
  sum(cur.execute("SELECT count(*) FROM parameter_value WHERE entity_id=?",(b[0],)).fetchone()[0] for b in bad))
c.close()
