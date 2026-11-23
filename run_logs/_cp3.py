import os,re,collections
from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
I=re.compile(r"^((BE|NL)C\d)_(\w+?)_((BE|NL)C\d)$")
Z={"BE":[f"BEC{i}" for i in range(1,9)],"NL":[f"NLC{i}" for i in range(1,10)]}
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    nodes={e["name"] for e in db.get_entity_items(entity_class_name="node")}
    edges=collections.defaultdict(set)
    for e in db.get_entity_items(entity_class_name="connection"):
        m=I.match(e["name"])
        if m and m.group(2)==m.group(5): edges[(m.group(2),m.group(3))].add((m.group(1),m.group(4)))
    for (c,car),E in sorted(edges.items()):
        zs=[z for z in Z[c] if f"{car}_{z}" in nodes]
        adj=collections.defaultdict(set)
        for a,b in E: adj[a].add(b); adj[b].add(a)
        seen={zs[0]}; st=[zs[0]]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        print(c,car,"zones with node",len(zs),"reachable",len(seen&set(zs)),"missing",sorted(set(zs)-seen))
