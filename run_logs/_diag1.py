import csv, collections
rows = list(csv.DictReader(open("data/Energy_Conversion/powerplants.csv",
            newline="", encoding="utf-8", errors="replace")))
nlbe = [r for r in rows if r["Country"] in ("Belgium", "Netherlands")]
def f(x):
    try:
        return float(x)
    except Exception:
        return None
din = [f(r["DateIn"]) for r in nlbe]
dout = [f(r["DateOut"]) for r in nlbe]
print("plants", len(nlbe))
print("DateIn  numeric:", sum(1 for x in din if x is not None))
print("DateOut numeric:", sum(1 for x in dout if x is not None))
ok = [x for x in din if x]
print("DateIn  range: %.0f .. %.0f" % (min(ok), max(ok)))
ok2 = [x for x in dout if x]
print("DateOut range: %.0f .. %.0f" % (min(ok2), max(ok2)))
print()
# branch 1 dominates: if date_out set, capacity=0 for every milestone >= date_out
print("DateOut distribution (branch 1 decides alone):")
for k, v in sorted(collections.Counter(int(x) for x in ok2).items()):
    print("   %d : %d plants" % (k, v))
print()
print("How many DateOut are BEFORE 2030? ->",
      sum(1 for x in ok2 if x <= 2030), "of", len(ok2))
