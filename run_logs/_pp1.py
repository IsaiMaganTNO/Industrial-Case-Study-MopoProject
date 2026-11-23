import csv, collections
p = "data/Energy_Conversion/powerplants.csv"
with open(p, newline="", encoding="utf-8", errors="replace") as f:
    r = csv.DictReader(f)
    cols = r.fieldnames
    print("columns:", cols)
    rows = list(r)
print("total rows", len(rows))
cand = [c for c in cols if "ate" in c.lower() or "life" in c.lower()
        or "country" in c.lower() or "capac" in c.lower() or "fuel" in c.lower()]
print("relevant cols:", cand)
