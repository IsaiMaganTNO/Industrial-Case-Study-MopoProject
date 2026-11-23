import csv, collections
p = r"data/Energy_Conversion/powerplants.csv"
with open(p, encoding="utf-8", errors="replace") as f:
    head = f.readline()
print("RAW HEADER:", head[:300])
delim = ";" if head.count(";") > head.count(",") else ","
print("delimiter chosen:", repr(delim))
with open(p, encoding="utf-8", errors="replace") as f:
    r = csv.DictReader(f, delimiter=delim)
    print("FIELDS:", r.fieldnames)
    cnt = collections.Counter()
    cap = collections.Counter()
    n = 0
    for row in r:
        n += 1
        c = (row.get("Country") or row.get("country") or "?").strip()
        cnt[c] += 1
        try: cap[c] += float(row.get("Capacity") or row.get("capacity") or 0)
        except ValueError: pass
print("total rows", n, "distinct countries", len(cnt))
for c, v in cnt.most_common(30):
    print("  %-28s n=%-7d cap=%.0f" % (c, v, cap[c]))
