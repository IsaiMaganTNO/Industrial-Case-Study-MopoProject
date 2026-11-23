import pandas as pd
# active scenario uses wy2009 (per docs). Is 2009 present in the new files?
for tag, p in [("STAGED", "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"),
               ("PRE",    "backups/data-pre-mixedres/VRE/VRE_time_series/wind-on-SP199-HH100.csv")]:
    d = pd.read_csv(p, usecols=[0], dtype=str)
    t = d.iloc[:, 0].astype(str).str.strip()
    g = t[t != ";"]
    yrs = g.str.extract(r"(\d{4})")[0].dropna()
    u = sorted(yrs.unique())
    print("%-7s distinct years: %d  range %s..%s" % (tag, len(u), u[0], u[-1]))
    print("        2009 present:", "2009" in set(u),
          "| count:", int((yrs == "2009").sum()))
    miss = [y for y in map(str, range(1980, 2025)) if y not in set(u)]
    print("        MISSING years:", miss)
