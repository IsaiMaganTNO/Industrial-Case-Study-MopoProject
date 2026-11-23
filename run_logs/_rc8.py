import os,glob
b=r"backups/data-pre-mixedres/VRE/VRE_time_series"
print("backup exists:", os.path.isdir(b))
for p in sorted(glob.glob(b+"/*.csv"))[:3]:
    with open(p,encoding="utf-8",errors="replace") as f:
        h=f.readline().rstrip(); r=[f.readline().rstrip() for _ in range(2)]
    print("==",os.path.basename(p)); print("   ",h[:60]); [print("    row:",x[:50]) for x in r]
# where does the format change in the staged file?
p=r"data/VRE/VRE_time_series/wind-on-SP277-HH150.csv"
import itertools
with open(p,encoding="utf-8",errors="replace") as f:
    f.readline()
    prev=None
    for i,line in enumerate(f):
        t=line.split(",")[0]
        style = "slash" if "/" in t else ("dash" if "-" in t else "other")
        if style!=prev:
            print("   line %d: style=%s  %r" % (i,style,t[:30]))
            prev=style
        if i>400000: break
