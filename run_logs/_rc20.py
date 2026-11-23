import sqlite3,re
p=r".spinetoolbox\items\ines_db\ines_db.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
ents=c.execute("SELECT count(*) FROM entity").fetchone()[0]
pvs=c.execute("SELECT count(*) FROM parameter_value").fetchone()[0]
print("INES_DB entities=%d parameter_values=%d  (baseline 14,966 / 20,984)"%(ents,pvs))
nodes=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='node'")]
T=("DE","DK","NO","UK")
EXTRA={'AL','AT','BA','BG','CH','CY','CZ','EE','ES','FI','FR','GR','HR','HU','IE','IT','LT','LU','LV','MD','MK','MT','PL','PT','RO','RS','SE','SI','SK','TR','UA'}
suf=lambda n: n.rsplit("_",1)[-1]
import collections
cnt=collections.Counter(suf(n) for n in nodes)
print("\nnodes by region suffix:")
tg={k:v for k,v in cnt.items() if k in T}
ic={k:v for k,v in cnt.items() if re.match(r"^(BEC|NLC)\d$",k)}
lk={k:v for k,v in cnt.items() if k in EXTRA}
print("   targets:",tg)
print("   IC1 total nodes:",sum(ic.values()),"across",len(ic),"regions")
print("   P4 LEAKED extra countries:",lk or "NONE")
c.close()
