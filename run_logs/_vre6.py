import pandas as pd
for tag, p in [("STAGED(new)", "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"),
               ("PRE-STAGING", "backups/data-pre-mixedres/VRE/VRE_time_series/wind-on-SP199-HH100.csv")]:
    d = pd.read_csv(p, usecols=[0, 1], dtype=str)
    t = d.iloc[:, 0].astype(str).str.strip()
    junk = (t == ";").sum()
    print("%-12s rows=%7d junk=%6d good=%7d  good/8760=%.2f"
          % (tag, len(d), junk, len(d)-junk, (len(d)-junk)/8760))
    g = d[t != ";"]
    print("              first=%s  last=%s" % (g.iloc[0, 0], g.iloc[-1, 0]))
