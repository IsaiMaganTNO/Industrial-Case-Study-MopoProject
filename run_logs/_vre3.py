import pandas as pd
p = "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
d = pd.read_csv(p, nrows=5)
print("shape(5 rows):", d.shape)
print("first col:", d.columns[0], "| sample:", list(d.iloc[:3, 0]))
sub = d[["DE01", "DE02", "NOS1", "UK01", "BEC1"]]
print(sub.to_string())
print()
d2 = pd.read_csv(p, usecols=["time", "DE01"])
print("total rows:", len(d2))
print("DE01 min %.4f max %.4f mean %.4f" % (d2.DE01.min(), d2.DE01.max(), d2.DE01.mean()))
print("time first:", d2.time.iloc[0], "last:", d2.time.iloc[-1])
