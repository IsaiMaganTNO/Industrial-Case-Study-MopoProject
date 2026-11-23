import csv, io, os

def header(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        line = f.readline().rstrip("\n").rstrip("\r")
    # verify delimiter by inspection, not by counting (known pitfall)
    print("   RAW[:160]:", line[:160])
    for d in [",", ";"]:
        n = len(next(csv.reader(io.StringIO(line), delimiter=d)))
        print("      delim %r -> %d fields" % (d, n))
    return line

for tag, p in [
    ("ACTIVE", "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"),
    ("NEW",    "verification/Data - IC1 and PECD1/VRE/VRE_time_series/wind-on-SP199-HH100.csv"),
]:
    print("===", tag, "%.0f MB" % (os.path.getsize(p)/1e6))
    header(p)
    print()
