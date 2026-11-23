import csv, collections
rows = list(csv.DictReader(open("data/Energy_Conversion/powerplants.csv",
            newline="", encoding="utf-8", errors="replace")))
nlbe = [r for r in rows if r["Country"] in ("Belgium", "Netherlands")]
def f(x):
    try:
        return float(x)
    except Exception:
        return None
# distribution of DateIn by fueltype, and implied retirement for plausible lifetimes
print("DateIn percentiles by fueltype (NL+BE):")
by = collections.defaultdict(list)
for r in nlbe:
    d = f(r["DateIn"])
    if d:
        by[r["Fueltype"]].append((d, f(r["Capacity"]) or 0))
for ft in sorted(by):
    ds = sorted(x[0] for x in by[ft])
    cap = sum(x[1] for x in by[ft])
    med = ds[len(ds)//2]
    print("  %-16s n=%3d medianDateIn=%4.0f  cap=%8.0f MW  +25y=%4.0f +40y=%4.0f"
          % (ft[:16], len(ds), med, cap, med+25, med+40))
