p = "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
with open(p, "rb") as f:
    f.seek(0, 2)
    size = f.tell()
    f.seek(max(0, size - 1200))
    tail = f.read().decode("utf-8", "replace")
lines = tail.splitlines()
print("LAST 5 LINES (repr, truncated):")
for L in lines[-5:]:
    print("   ", repr(L[:110]))
print()
print("394032 / 8760 = %.2f weather years" % (394032/8760))
print("394032 / 8766 = %.2f" % (394032/8766))
