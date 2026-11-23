import sqlite3, collections
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def pairs(cls):
    out=collections.defaultdict(list)
    for conn,node in c.execute("""
      select e2.name, e3.name from entity e
      join entity_class ec on ec.id=e.class_id
      join entity_element el on el.entity_id=e.id
      join entity e2 on e2.id=el.element_id
      join entity_element el2 on el2.entity_id=e.id
      join entity e3 on e3.id=el2.element_id
      where ec.name=? and el.position=0 and el2.position=1
    """,(cls,)):
        out[conn].append(node)
    return out
fr=pairs('connection__from_node'); to=pairs('connection__to_node')
co2=[r[0] for r in c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='connection' and e.name like '%CO2%'""")]
dirg=collections.defaultdict(set); undir=collections.defaultdict(set)
for k in co2:
    for a in fr.get(k,[]):
        for b in to.get(k,[]):
            dirg[a].add(b); undir[a].add(b); undir[b].add(a)
def bfs(g,s):
    seen={s}; st=[s]
    while st:
        n=st.pop()
        for m in g.get(n,()):
            if m not in seen: seen.add(m); st.append(m)
    return seen
sinks={'CO2_NLC1','CO2_NLC5','CO2_NLC6'}
for s in ['CO2_BEC6','CO2_BEC7','CO2_NLC5','CO2_NLC6']:
    d=bfs(dirg,s); u=bfs(undir,s)
    print(f"{s}: directed={len(d)} reaches_injector={sorted(sinks&d)} | undirected={len(u)} reaches={sorted(sinks&u)}")
print()
print("in-edges to injector regions:")
for n in sorted(sinks):
    print("  ",n,"<-",sorted([a for a,bs in dirg.items() if n in bs]))
