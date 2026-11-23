import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
# does CCGT+CC share any entity with CCGT, or is it fully independent?
for fam in ("CCGT","CCGT+CC"):
    ins=set();outs=set()
    for (n,) in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='node__to_unit'"):
        nd,u=n.split("__",1)
        if base(u)==fam: ins.add(base(nd))
    for (n,) in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='unit__to_node'"):
        u,nd=n.split("__",1)
        if base(u)==fam: outs.add(base(nd))
    cnt=c.execute("SELECT COUNT(*) FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='unit' AND e.name LIKE ?",(fam+"\\_%",)).fetchone()[0]
    print("%-9s units=%-3d IN=%s OUT=%s"%(fam,cnt,sorted(ins),sorted(outs)))
