import pandas as pd, numpy as np

def load2009(p, cols):
    d = pd.read_csv(p, usecols=["time"] + cols, dtype={"time": str})
    t = d.time.astype(str).str.strip()
    d = d[t != ";"].copy()
    d["yr"] = d.time.str.extract(r"(\d{4})")[0]
    return d[d.yr == "2009"].reset_index(drop=True)

cols = ["BEC1", "NLC6", "BEC8"]
a = load2009("data/VRE/VRE_time_series/wind-on-SP199-HH100.csv", cols)
b = load2009("backups/data-pre-mixedres/VRE/VRE_time_series/wind-on-SP199-HH100.csv", cols)
print("staged 2009 rows:", len(a), " pre 2009 rows:", len(b))
for c in cols:
    x, y = a[c].to_numpy(float), b[c].to_numpy(float)
    n = min(len(x), len(y))
    same = np.allclose(x[:n], y[:n], atol=1e-9)
    print("  %-6s identical=%-5s  mean %.5f vs %.5f  maxdiff %.2e"
          % (c, same, x[:n].mean(), y[:n].mean(), np.abs(x[:n]-y[:n]).max()))
