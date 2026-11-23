import sqlite3, collections, re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
c=sqlite3.connect(db)
rows=[r[0] for r in c.execute("select e.name from entity e join entity_class k on k.id=e.class_id where k.name=\"node\"")]
print("nodes:",len(rows))
suf=collections.Counter()
for n in rows:
    m=re.search(r"_([A-Z]{2}(?:C\d)?)$", n)
    suf[m.group(1) if m else "<none>"]+=1
for k,v in sorted(suf.items(), key=lambda x:-x[1])[:40]:
    print(f"  {k:8} {v}")
# which commodities exist at bare country level
for cc in ["DE","FR","UK","LU","NO","DK"]:
    hits=[n for n in rows if n.endswith("_"+cc)]
    print(cc, sorted(hits))
