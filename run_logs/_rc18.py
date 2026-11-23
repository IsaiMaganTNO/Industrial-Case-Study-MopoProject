import sqlite3
p=r".spinetoolbox\items\gas_db\gas_db.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
EXTRA={'AL','AT','BA','BG','CH','CY','CZ','EE','ES','FI','FR','GR','HR','HU','IE','IT','LT','LU','LV','MD','MK','MT','PL','PT','RO','RS','SE','SI','SK','TR','UA'}
# find multi-dimensional entities whose element list touches an extra region
q="""SELECT ec.name, e.id, e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id"""
hits={}
for cls,eid,nm in c.execute(q):
    els=[r[0] for r in c.execute("""SELECT e2.name FROM entity_element ee
         JOIN entity e2 ON e2.id=ee.element_id WHERE ee.entity_id=?""",(eid,))]
    if set(els)&EXTRA:
        hits.setdefault(cls,0); hits[cls]+=1
print("multi-dim entities touching an extra region, by class:")
for k,v in sorted(hits.items(),key=lambda x:-x[1]): print("   %-50s %d"%(k,v))
print("total:",sum(hits.values()))
c.close()
