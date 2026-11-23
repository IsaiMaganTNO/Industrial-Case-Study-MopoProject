import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
# build CO2 pipeline graph, check BE -> NLC1/5/6 reachability
edges=set()
for (x,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='connection' AND e.name LIKE '%CO2%'"""):
    p=x.split("_CO2_")
    if len(p)==2: edges.add((p[0],p[1]))
import collections
adj=collections.defaultdict(set)
for a,b in edges: adj[a].add(b); adj[b].add(a)
sinks={"NLC1","NLC5","NLC6"}
def reach(s):
    seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); st.append(v)
    return seen
for r in ("BEC6","BEC7","NLC5","NLC6"):
    rr=reach(r)
    print("%-6s reaches injector region? %s   (nodes=%d)"%(r,bool(rr&sinks),len(rr)))
print("\ntotal CO2 edges:",len(edges))
