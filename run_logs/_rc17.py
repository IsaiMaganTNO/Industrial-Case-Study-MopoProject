import sqlite3,os
p=r".spinetoolbox\items\gas_db\gas_db.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
rows=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'")]
KEEP=set(["BEC%d"%i for i in range(1,9)]+["NLC%d"%i for i in range(1,10)]+["DE","DK","NO","UK"])
extra=sorted(set(rows)-KEEP)
print("extra regions (%d):"%len(extra), extra)
# do they carry parameter values?
q="""SELECT e.name, count(*) FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id WHERE e.name IN (%s) GROUP BY e.name ORDER BY 2 DESC"""%(",".join("?"*len(extra)))
print("\nregion entities with pvals:")
for n,k in c.execute(q,extra).fetchall()[:10]: print("   ",n,k)
# multi-dim entities referencing extras (e.g. network links)
print("\nentities whose byname includes an extra region:")
q2="""SELECT ec.name, count(*) FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE e.name LIKE '%,%' GROUP BY ec.name ORDER BY 2 DESC"""
for n,k in c.execute(q2).fetchall()[:12]: print("   %-45s %d"%(n,k))
c.close()
