import os
root = "data"
rows=[]
for dp,_,fs in os.walk(root):
    for f in fs:
        p=os.path.join(dp,f)
        if f.lower().endswith((".bak",)): continue
        rows.append((os.path.relpath(p,root), os.path.getsize(p)))
print("total files under data/:", len(rows))
# group by top dir
import collections
g=collections.defaultdict(list)
for r,s in rows: g[r.split(os.sep)[0]].append((r,s))
for k in sorted(g):
    print("\n=== %s (%d files)" % (k, len(g[k])))
    for r,s in sorted(g[k])[:18]:
        print("   %-70s %10d" % (r, s))
    if len(g[k])>18: print("   ... +%d more" % (len(g[k])-18))
