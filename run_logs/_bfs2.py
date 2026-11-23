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
g=collections.defaultdict(set)
for k in co2:
    for a in fr.get(k,[]):
        for b in to.get(k,[]): g[a].add(b)
def bfs(s):
    seen={s}; st=[s]
    while st:
        n=st.pop()
        for m in g.get(n,()):
            if m not in seen: seen.add(m); st.append(m)
    return seen
print("BEC7 directed closure:",sorted(bfs('CO2_BEC7')))
# which nodes host an injector unit?
inj=collections.defaultdict(list)
for u,n in c.execute("""
  select e2.name,e3.name from entity e
  join entity_class ec on ec.id=e.class_id
  join entity_element el on el.entity_id=e.id and el.position=0
  join entity e2 on e2.id=el.element_id
  join entity_element el2 on el2.entity_id=e.id and el2.position=1
  join entity e3 on e3.id=el2.element_id
  where ec.name='node__to_unit' and e2.name like 'CO2_%'"""):
    if 'injection' in n: inj[u].append(n)
print("\nnodes feeding injectors:",dict(inj))
print("\nany injector reachable from BEC7?", sorted(set(inj)&bfs('CO2_BEC7')))
print("any injector reachable from BEC6?", sorted(set(inj)&bfs('CO2_BEC6')))
