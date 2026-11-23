import json, collections
d = json.load(open(".spinetoolbox/project.json", encoding="utf-8"))
items = d["items"]
conns = d["project"]["connections"]
print("connections", len(conns), "jumps", len(d["project"].get("jumps", [])))
adj = collections.defaultdict(set)
indeg = {n: 0 for n in items}
for c in conns:
    f, t = c["from"][0], c["to"][0]
    if t not in adj[f]:
        adj[f].add(t); indeg[t] += 1
q = sorted([n for n in items if indeg[n] == 0])
order, ind = [], dict(indeg)
while q:
    n = q.pop(0); order.append(n)
    for m in sorted(adj[n]):
        ind[m] -= 1
        if ind[m] == 0:
            q.append(m); q.sort()
print("topo", len(order), "of", len(items))
for i, n in enumerate(order):
    print("%3d %-22s %-16s -> %s" % (i, n[:22], items[n]["type"],
          ",".join(sorted(adj[n]))[:48]))
