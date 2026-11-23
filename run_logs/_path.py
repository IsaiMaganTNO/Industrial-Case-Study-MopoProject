import sqlite3, collections, heapq
def graph(db):
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
    cost={}
    for conn,v in c.execute("""select cc.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id
      join entity_element el on el.entity_id=e.id and el.position=0
      join entity cc on cc.id=el.element_id
      where pd.name='connection_flow_cost'"""):
        cost[conn]=float(bytes(v).decode())
    g=collections.defaultdict(list)
    for k in [r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection' and e.name like '%!_CO2!_%' escape '!'")]:
        for a in fr.get(k,[]):
            for b in to.get(k,[]): g[a].append((b,cost.get(k,0.0),k))
    return g
def dij(g,s,targets):
    dist={s:0.0}; prev={}; pq=[(0.0,s)]
    while pq:
        d,n=heapq.heappop(pq)
        if d>dist.get(n,1e18): continue
        for m,w,k in g.get(n,()):
            nd=d+w
            if nd<dist.get(m,1e18): dist[m]=nd; prev[m]=(n,k); heapq.heappush(pq,(nd,m))
    out={}
    for t in targets:
        if t in dist:
            path=[]; cur=t
            while cur!=s: p,k=prev[cur]; path.append(cur); cur=p
            out[t]=(dist[t],list(reversed(path)))
    return out
sinks=['CO2_NLC1','CO2_NLC5','CO2_NLC6']
for tag,db in [("BEFORE",r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"),
               ("AFTER ",r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")]:
    g=graph(db)
    print(f"=== {tag}")
    for src in ["CO2_BEC7","CO2_BEC6"]:
        r=dij(g,src,sinks)
        if not r: print(f"  {src}: NO ROUTE TO ANY INJECTOR")
        for t,(d,p) in sorted(r.items(),key=lambda x:x[1][0]):
            print(f"  {src} -> {t}: cost={d:.6f}  hops={len(p)}  {' -> '.join(x.replace('CO2_','') for x in [src]+p)}")
