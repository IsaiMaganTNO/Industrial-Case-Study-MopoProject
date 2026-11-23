import pandas as pd, glob, os
print("=== output index sanity ===")
for p in sorted(glob.glob(r"data/VRE_NWEU/VRE_time_series/*.csv")):
    d=pd.read_csv(p,index_col=0,nrows=3)
    with open(p,encoding="utf-8") as f: f.readline(); first=f.readline().split(",")[0]
    print("  %-32s first=%s cols=%d" % (os.path.basename(p),first,len(d.columns)))
print("\n=== 2009 CF unchanged by the index fix? ===")
d=pd.read_csv(r"data/VRE_NWEU/VRE_time_series/wind-on-SP277-HH150.csv",index_col=0,parse_dates=True)
y=d[d.index.year==2009]
print("  2009 hours:",len(y))
print("  CF:",{k:round(y[k].mean(),3) for k in ["DE","DK","NO","UK","BEC1","NLC6"]})
print("  full index:",d.index[0],"->",d.index[-1],"unique:",d.index.is_unique)
print("  NaNs:",int(d.isna().sum().sum()))
