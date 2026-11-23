import sqlite3,collections
p=r".spinetoolbox\items\ines_db\ines_db.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
EXTRA={'AT','CH','CZ','FR','IE','LU','PL','SE','FI'}
rows=[(r[0],r[1]) for r in c.execute("SELECT ec.name,e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id")]
hits=[(cls,n) for cls,n in rows if n.rsplit("_",1)[-1] in EXTRA]
print("entities ending in a leaked country:",len(hits))
byc=collections.Counter(cls for cls,_ in hits)
for k,v in byc.most_common(): print("   %-28s %d"%(k,v))
print("\nsamples:")
for cls,n in hits[:25]: print("   %-20s %s"%(cls,n))
c.close()
