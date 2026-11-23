import pandas as pd
old=r"data/VRE/VRE_time_series/wind-on-SP277-HH150.csv"
new=r"data/VRE_NWEU/VRE_time_series/wind-on-SP277-HH150.csv"
for p in [old,new]:
    with open(p,encoding="utf-8",errors="replace") as f:
        h=f.readline().rstrip(); r=[f.readline().rstrip() for _ in range(2)]
    print("==",p)
    print("   header[:70]:",h[:70])
    for x in r: print("   row:",x[:70])
