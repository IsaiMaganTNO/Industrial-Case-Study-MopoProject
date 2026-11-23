for p in [r"data/Rdemand/other_electricity_demand.csv", r"data/Rdemand/other_electricity_demand_IC1.csv"]:
    with open(p, encoding="utf-8", errors="replace") as f:
        h = f.readline().rstrip("\n")
        r1 = f.readline().rstrip("\n")
    print("==", p)
    print("   RAW HEADER:", h[:260])
    print("   ROW1      :", r1[:160])
    d = ";" if h.count(";") > h.count(",") else ","
    cols = h.split(d)
    print("   delim", repr(d), "ncols", len(cols))
    tgt = [c for c in cols if c.strip().strip(chr(34)).upper() in ("DE","DK","NO","UK")]
    print("   country-level target cols present:", tgt)
    print("   sample cols:", [c.strip()[:12] for c in cols[:14]])
