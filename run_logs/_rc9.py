p=r"data/VRE/VRE_time_series/wind-on-SP277-HH150.csv"
with open(p,encoding="utf-8",errors="replace") as f:
    f.readline()
    rows=[f.readline().split(",")[0] for _ in range(30)]
print("first 30 timestamps:", rows)
print("distinct in first 30:", len(set(rows)))
# how many consecutive rows share a date?
from collections import Counter
with open(p,encoding="utf-8",errors="replace") as f:
    f.readline()
    c=Counter()
    for i,line in enumerate(f):
        c[line.split(",")[0]]+=1
        if i>50000: break
print("rows per date (sample):", list(c.items())[:5])
