import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
print("atmosphere nodes:",c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='node' and e.name like '%atmosphere%'""").fetchall())
print()
# target units: HC consumers with NO atmosphere flow
atm=set(r[0].replace("__atmosphere","") for r in c.execute("""select e.name from entity e
 join entity_class ec on ec.id=e.class_id where ec.name='unit__to_node' and e.name like '%__atmosphere'"""))
tgt=[]
for (n,) in c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='node__to_unit' and e.name like 'HC\\_%' escape '\\'"""):
    node,u=n.split("__",1)
    if u not in atm: tgt.append((u,node,n))
import collections
print("target units:",len(tgt))
print(collections.Counter(u.rsplit("_",1)[0] for u,_,_ in tgt))
