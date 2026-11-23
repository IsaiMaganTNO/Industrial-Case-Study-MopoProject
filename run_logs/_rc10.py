for t in ["wind-on-SP199-HH100","solar-PV-no-tracking","wind-on-SP277-HH150"]:
    p=f"data/VRE/VRE_time_series/{t}.csv"
    with open(p,encoding="utf-8",errors="replace") as f:
        f.readline()
        rows=[f.readline().split(",")[0] for _ in range(3)]
    print("== %-22s first: %s" % (t, rows))
    # scan for style changes
    with open(p,encoding="utf-8",errors="replace") as f:
        f.readline(); prev=None
        for i,line in enumerate(f):
            s=line.split(",")[0]
            st=("slash" if "/" in s else "dash" if "-" in s else "junk")
            has_time=":" in s
            key=(st,has_time)
            if key!=prev:
                print("     line %7d %s time=%s %r" % (i,st,has_time,s[:26]))
                prev=key
