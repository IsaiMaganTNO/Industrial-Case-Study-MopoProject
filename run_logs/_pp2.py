import csv, collections
p = "data/Energy_Conversion/powerplants.csv"
with open(p, newline="", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
tot = collections.Counter(); rnd = collections.Counter()
cap_t = collections.defaultdict(float); cap_r = collections.defaultdict(float)
for r in rows:
    c = r["Country"]
    if c not in ("Belgium", "Netherlands"):
        continue
    try:
        cap = float(r["Capacity"] or 0)
    except ValueError:
        cap = 0.0
    tot[c] += 1; cap_t[c] += cap
    has_out = bool((r["DateOut"] or "").strip())
    has_in = bool((r["DateIn"] or "").strip())
    if not has_out and not has_in:
        rnd[c] += 1; cap_r[c] += cap
print("%-14s %8s %8s %8s | %12s %12s %7s" % ("country", "plants", "random", "pct",
      "cap_MW", "cap_rnd_MW", "pct"))
for c in sorted(tot):
    print("%-14s %8d %8d %7.1f%% | %12.0f %12.0f %6.1f%%" % (
        c, tot[c], rnd[c], 100*rnd[c]/tot[c], cap_t[c], cap_r[c],
        100*cap_r[c]/cap_t[c] if cap_t[c] else 0))
print()
print("NOTE: DateOut-only is the first branch; DateIn+lifetime second; else RANDOM.")
