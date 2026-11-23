import sqlite3,collections
c=sqlite3.connect(r".spinetoolbox\items\transport_db\transport_db.sqlite")
cur=c.cursor()
cls={r[0]:r[1] for r in cur.execute("SELECT id,name FROM entity_class")}
cnt=collections.Counter()
rows=[]
for eid,cid,nm in cur.execute("SELECT id,class_id,name FROM entity"):
    n=cur.execute("SELECT count(*) FROM entity_element WHERE entity_id=?",(eid,)).fetchone()[0]
    cnt[(cls[cid],n)]+=1
    if nm.split("__")[-1] in ("DE","DK","NO","UK"): rows.append((cls[cid],nm,n))
print("class/elementcount histogram:",dict(cnt))
print("\n4-country entities with element count:")
h=collections.Counter((c0,n) for c0,_,n in rows)
print(dict(h))
print("\nexamples of 2-element composites:")
for c0,nm,n in rows:
    if c0=="commodity__vehicle__region" and n!=3: print("   ",nm,n)
c.close()
