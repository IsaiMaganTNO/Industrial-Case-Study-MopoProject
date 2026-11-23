import sqlite3, collections
for tag,db in [("BEFORE",r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"),
               ("AFTER ",r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")]:
    c=sqlite3.connect(db)
    def pairs(cls):
        out=collections.defaultdict(list)
        for conn,node in c.execute("""
          select e2.name,e3.name from entity e
          join entity_class ec on ec.id=e.class_id
          join entity_element el on el.entity_id=e.id and el.position=0
          join entity e2 on e2.id=el.element_id
          join entity_element el2 on el2.entity_id=e.id and el2.position=1
          join entity e3 on e3.id=el2.element_id
          where ec.name=?""",(cls,)): out[conn].append(node)
        return out
    fr=pairs('connection__from_node'); to=pairs('connection__to_node')
    co2=[r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection' and e.name like '%!_CO2!_%' escape '!'")]
    g=collections.defaultdict(set); E=set()
    for k in co2:
        for a in fr.get(k,[]):
            for b in to.get(k,[]): g[a].add(b); E.add((a,b))
    rev=sum(1 for a,b in E if (b,a) in E)
    def bfs(s):
        seen={s}; st=[s]
        while st:
            n=st.pop()
            for m in g.get(n,()):
                if m not in seen: seen.add(m); st.append(m)
        return seen
    sinks={'CO2_NLC1','CO2_NLC5','CO2_NLC6'}
    print(f"--- {tag}: conns={len(co2)} edges={len(E)} reverse_twins={rev}")
    for s in ['CO2_BEC6','CO2_BEC7','CO2_BEC2','CO2_NLC5']:
        d=bfs(s); print(f"    {s}: closure={len(d):3d} injectors_reached={sorted(x[-5:] for x in sinks&d)}")
