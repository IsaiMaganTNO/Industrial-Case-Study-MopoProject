import pandas as pd, os, csv, io
base = "data/VRE/VRE_time_series"
print("%-32s %8s %7s %8s %8s" % ("file", "rows", "junk", "good", "yrs"))
for f in sorted(os.listdir(base)):
    p = os.path.join(base, f)
    d = pd.read_csv(p, usecols=[0], dtype=str)
    t = d.iloc[:, 0].astype(str).str.strip()
    junk = int((t == ";").sum())
    good = len(d) - junk
    print("%-32s %8d %7d %8d %8.2f" % (f[:32], len(d), junk, good, good/8760))
