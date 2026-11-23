import pandas as pd, numpy as np
SRC=r"data/VRE"; DST=r"data/VRE_NWEU"
w=pd.read_excel(r"data-pipelines/europe/_ines-builder/region_transformation.xlsx","PECD2_PECD1")
print("=== 1. availability factors in [0,1] and sane CF ===")
for t in ["wind-on-SP277-HH150","solar-PV-no-tracking","wind-on-existing"]:
    d=pd.read_csv(f"{DST}/VRE_time_series/{t}.csv",index_col=0,low_memory=False)
    d.index=pd.to_datetime(d.index,errors="coerce",dayfirst=True)
    d=d[~d.index.isna()]
    y=d[d.index.year==2009]
    print("\n%s  2009 hours=%d" % (t,len(y)))
    print("   min %.3f max %.3f  anyNaN=%s" % (d.min().min(), d.max().max(), bool(d.isna().any().any())))
    cf=y.mean().round(3)
    print("   2009 mean CF:", {k:cf[k] for k in ["DE","DK","NO","UK"] if k in cf})
    print("   BE/NL sample:", {k:cf[k] for k in ["BEC1","NLC1","NLC6"] if k in cf})
print("\n=== 2. country CF must lie within its members' range ===")
d_old=pd.read_csv(f"{SRC}/VRE_time_series/wind-on-SP277-HH150.csv",index_col=0,low_memory=False)
d_old.index=pd.to_datetime(d_old.index,errors="coerce",dayfirst=True)
d_old=d_old[~d_old.index.isna()]
o=d_old[d_old.index.year==2009].apply(pd.to_numeric,errors="coerce")
d_new=pd.read_csv(f"{DST}/VRE_time_series/wind-on-SP277-HH150.csv",index_col=0,low_memory=False)
d_new.index=pd.to_datetime(d_new.index,errors="coerce",dayfirst=True)
n=d_new[d_new.index.year==2009]
for c in ["DE","DK","NO","UK"]:
    mem=w[w.target==c].set_index("source")["capacity"].to_dict()
    mem={k:v for k,v in mem.items() if k in o.columns}
    cfs={k:o[k].mean() for k in mem}
    agg=n[c].mean()
    ok = min(cfs.values())-1e-6 <= agg <= max(cfs.values())+1e-6
    print("  %s agg=%.4f  members %.4f..%.4f  within=%s" % (c,agg,min(cfs.values()),max(cfs.values()),ok))
    # independent recompute
    tot=sum(mem.values()); man=sum(o[k]*(mem[k]/tot) for k in mem).mean()
    print("      manual weighted mean=%.4f  delta=%.2e" % (man, abs(man-agg)))
