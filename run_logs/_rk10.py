import sqlite3,collections
c=sqlite3.connect(r".spinetoolbox\items\transport_db\transport_db.sqlite")
cur=c.cursor()
cls={r[0]:r[1] for r in cur.execute("SELECT id,name FROM entity_class")}
ents=cur.execute("SELECT id,class_id,name FROM entity").fetchall()   # materialise first
ecount=collections.Counter(r[0] for r in cur.execute("SELECT entity_id FROM entity_element").fetchall())
bad=[(nm,cls[cid],ecount.get(eid,0)) for eid,cid,nm in ents
     if cls[cid]=="commodity__vehicle__region" and ecount.get(eid,0)!=3]
print("malformed composites:",len(bad))
for b in bad[:8]: print("   ",b)
pv=collections.Counter(r[0] for r in cur.execute("SELECT entity_id FROM parameter_value").fetchall())
ids={eid for eid,cid,nm in ents if cls[cid]=="commodity__vehicle__region" and ecount.get(eid,0)!=3}
print("parameter_values on malformed:",sum(pv.get(i,0) for i in ids))
print("\nvehicle entities present:",sorted(nm for eid,cid,nm in ents if cls[cid]=="vehicle"))
print("\ncommodity entities present:",sorted(nm for eid,cid,nm in ents if cls[cid]=="commodity"))
c.close()
