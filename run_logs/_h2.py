import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
prod={}
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit__to_node'"""):
    u,nd=n.split("__",1)
    if base(nd)=="H2": prod.setdefault(base(u),0); prod[base(u)]+=1
print("units PRODUCING into H2 node:")
for k,v in sorted(prod.items()): print("   %-26s %d"%(k,v))
cons={}
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit'"""):
    nd,u=n.split("__",1)
    if base(nd)=="H2": cons.setdefault(base(u),0); cons[base(u)]+=1
print("\nunits CONSUMING H2 node:",len(cons))
for k,v in sorted(cons.items()): print("   %-26s %d"%(k,v))
