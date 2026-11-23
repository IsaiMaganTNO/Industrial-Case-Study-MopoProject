import json, collections
d = json.load(open(".spinetoolbox/project.json", encoding="utf-8"))
items = d.get("items", {})
conns = d.get("connections", [])
print("connections", len(conns))
adj = collections.defaultdict(list)
indeg = collections.Counter({n: 0 for n in items})
for c in conns:
    f = c["from"][0]; t = c["to"][0]
    adj[f].append(t); indeg[t] += 1
# topological order
q = sorted([n for n in items if indeg[n] == 0])
order = []
indeg2 = dict(indeg)
while q:
    n = q.pop(0); order.append(n)
    for m in sorted(adj[n]):
        indeg2[m] -= 1
        if indeg2[m] == 0:
            q.append(m); q.sort()
print("topo len", len(order), "of", len(items))
for i, n in enumerate(order):
    print("%3d %-24s %-16s -> %s" % (i, n[:24], items[n].get("type"),
          ",".join(sorted(adj[n]))[:46]))
