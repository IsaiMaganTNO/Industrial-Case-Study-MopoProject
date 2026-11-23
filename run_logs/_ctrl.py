import sqlite3, collections
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def pairs(cls):
    out=collections.defaultdict(list)
    for conn,node in c.execute("""
      select e2.name, e3.name from entity e
      join entity_class ec on ec.id=e.class_id
      join entity_element el on el.entity_id=e.id and el.position=0
      join entity e2 on e2.id=el.element_id
      join entity_element el2 on el2.entity_id=e.id and el2.position=1
      join entity e3 on e3.id=el2.element_id
      where ec.name=?""",(cls,)):
        out[conn].append(node)
    return out
fr=pairs('connection__from_node'); to=pairs('connection__to_node')
allc=[r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection'")]
grp=collections.defaultdict(list)
for k in allc:
    grp['CO2' if 'CO2' in k else 'other'].append(k)
for g,ks in grp.items():
    E=set()
    for k in ks:
        for a in fr.get(k,[]):
            for b in to.get(k,[]): E.add((a,b))
    rev=sum(1 for a,b in E if (b,a) in E)
    multi=sum(1 for k in ks if len(fr.get(k,[]))>1 or len(to.get(k,[]))>1)
    print(f"{g:6s} conns={len(ks):4d} edges={len(E):4d} with_reverse_twin={rev:4d} multi_from/to={multi}")
# sample a few non-CO2 connection names
print("\nsample other conns:",grp['other'][:6])
