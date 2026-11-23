import csv, collections
rows = list(csv.DictReader(open("data/Energy_Conversion/powerplants.csv",
            newline="", encoding="utf-8", errors="replace")))
# Replicate pipeline branch logic. Note L1345 uses unit["date_in"] but then
# reads unit["DateIn"] -- so branch 2 depends on date_in truthiness.
tot = collections.Counter(); b1 = collections.Counter()
b2 = collections.Counter(); b3 = collections.Counter()
cap = collections.defaultdict(float); cap3 = collections.defaultdict(float)
big3 = []
for r in rows:
    c = r["Country"]
    if c not in ("Belgium", "Netherlands"):
        continue
    try:
        mw = float(r["Capacity"] or 0)
    except ValueError:
        mw = 0.0
    tot[c] += 1; cap[c] += mw
    has_out = bool((r["DateOut"] or "").strip())
    has_in = bool((r["DateIn"] or "").strip())
    if has_out:
        b1[c] += 1
    elif has_in:
        b2[c] += 1          # requires lifetime too; if absent -> falls to else
    else:
        b3[c] += 1; cap3[c] += mw
        big3.append((mw, c, r["Fueltype"], r["Technology"], r["Name"][:26]))
print("%-13s %7s %7s %7s %7s | %10s %10s %6s" % ("country","tot","dOut","dIn","NEITHER","cap_MW","cap_neither","pct"))
for c in sorted(tot):
    print("%-13s %7d %7d %7d %7d | %10.0f %10.0f %5.1f%%" % (
        c, tot[c], b1[c], b2[c], b3[c], cap[c], cap3[c], 100*cap3[c]/cap[c]))
print()
print("Largest NEITHER-branch plants (random retirement):")
for mw, c, ft, tech, nm in sorted(big3, reverse=True)[:12]:
    print("  %8.1f MW  %-12s %-12s %-14s %s" % (mw, c[:12], ft[:12], str(tech)[:14], nm))
