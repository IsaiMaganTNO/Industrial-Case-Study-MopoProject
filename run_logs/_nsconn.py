import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# nodes in NS zones
ns=[n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"node\" and e.name like \"%NSNL%\" or e.name like \"%NSBE%\"")]
print("NS nodes:",ns)
def rel(cls):
    out=[]
    for ename, in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=?",(cls,)):
        out.append(ename)
    return out
for cls in ["connection__from_node","connection__to_node"]:
    rs=[r for r in rel(cls) if "NS" in r]
    print(cls,len(rs))
    for r in rs[:40]: print("   ",r)
