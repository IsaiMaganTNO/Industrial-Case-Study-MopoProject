import csv, collections
rows = list(csv.DictReader(open("data/Energy_Conversion/powerplants.csv",
            newline="", encoding="utf-8", errors="replace")))
sel = collections.defaultdict(float)
for r in rows:
    if r["Country"] not in ("Belgium", "Netherlands"):
        continue
    try:
        mw = float(r["Capacity"] or 0)
    except ValueError:
        mw = 0.0
    has_out = bool((r["DateOut"] or "").strip())
    has_in = bool((r["DateIn"] or "").strip())
    br = "dOut" if has_out else ("dIn" if has_in else "NEITHER")
    ft = (r["Fueltype"] or "?")
    sel[(ft, br)] += mw
fts = sorted({k[0] for k in sel})
print("%-16s %12s %12s %12s" % ("fueltype", "dOut_MW", "dIn_MW", "NEITHER_MW"))
for ft in fts:
    a = sel.get((ft, "dOut"), 0); b = sel.get((ft, "dIn"), 0)
    c = sel.get((ft, "NEITHER"), 0)
    if a + b + c > 1:
        print("%-16s %12.0f %12.0f %12.0f" % (ft[:16], a, b, c))
