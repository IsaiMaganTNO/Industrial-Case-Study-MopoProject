import csv, io, os, collections
base = "data/VRE/VRE_time_series"
for f in sorted(os.listdir(base)):
    p = os.path.join(base, f)
    with open(p, encoding="utf-8", errors="replace") as fh:
        hdr = next(csv.reader(io.StringIO(fh.readline())))
    cols = hdr[1:]
    ic1 = sum(1 for c in cols if c.startswith(("BEC", "NLC")))
    off = sum(1 for c in cols if c.startswith(("NS", "BAL", "ATL", "MED", "OFF")))
    pre = collections.Counter(c[:2] for c in cols
                              if not c.startswith(("BEC", "NLC")))
    tgt = sum(pre.get(k, 0) for k in ["DE", "DK", "NO", "UK"])
    print("%-32s cols=%4d IC1=%3d off=%3d DE/DK/NO/UK=%2d"
          % (f[:32], len(cols), ic1, off, tgt))
