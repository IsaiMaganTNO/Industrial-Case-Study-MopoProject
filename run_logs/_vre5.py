import pandas as pd
p = "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
d = pd.read_csv(p, usecols=["time", "DE01"], dtype=str)
bad = d[d.time.astype(str).str.strip() == ";"]
good = d[d.time.astype(str).str.strip() != ";"]
print("total rows  :", len(d))
print("junk ';' rows:", len(bad))
print("good rows   :", len(good))
print("good/8760   : %.3f" % (len(good)/8760))
print()
print("DE01 on junk rows unique:", bad.DE01.unique()[:5])
print("first good time:", good.time.iloc[0], "last good:", good.time.iloc[-1])
