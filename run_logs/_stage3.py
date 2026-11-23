import csv, io, collections

p = "verification/Data - IC1 and PECD1/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
with open(p, "r", encoding="utf-8", errors="replace") as f:
    hdr = next(csv.reader(io.StringIO(f.readline())))
cols = hdr[1:]
print("total region columns:", len(cols))
ic1 = [c for c in cols if c.startswith(("BEC", "NLC"))]
print("IC1 clusters:", len(ic1))
rest = [c for c in cols if c not in ic1]
print("PECD2 regions:", len(rest))
pre = collections.defaultdict(list)
for c in rest:
    pre[c[:2]].append(c)
print()
print("TARGET COUNTRIES:")
for k in ["DE", "DK", "NO", "UK"]:
    print("  %-3s %2d -> %s" % (k, len(pre.get(k, [])), sorted(pre.get(k, []))))
print()
print("all prefixes:", {k: len(v) for k, v in sorted(pre.items())})
