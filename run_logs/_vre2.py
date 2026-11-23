import csv, io
def cols(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return next(csv.reader(io.StringIO(fh.readline())))[1:]
a = cols("data/VRE/VRE_time_series/wind-on-SP199-HH100.csv")
b = cols("data/VRE/VRE_time_series/wind-on-existing.csv")
ia = {c for c in a if c.startswith(("BEC", "NLC"))}
ib = {c for c in b if c.startswith(("BEC", "NLC"))}
print("full file IC1:", len(ia))
print("existing  IC1:", len(ib))
print("MISSING from wind-on-existing:", sorted(ia - ib))
print()
# was this also true BEFORE staging?
import os
old = "backups/data-pre-mixedres/VRE/VRE_time_series/wind-on-existing.csv"
if os.path.exists(old):
    c = cols(old)
    io_ = {x for x in c if x.startswith(("BEC", "NLC"))}
    print("PRE-STAGING wind-on-existing IC1:", len(io_))
    print("  missing then:", sorted(ia - io_))
    print("  => pre-existing condition, not caused by staging:", (ia - io_) == (ia - ib))
