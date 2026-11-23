import pandas as pd, numpy as np, glob, os
out=[]
for p in sorted(glob.glob(r"data/VRE/VRE_time_series/*.csv")):
    s=pd.read_csv(p,index_col=0,usecols=[0],low_memory=False)
    idx=pd.Series(s.index.astype(str))
    idx=idx[~idx.str.startswith(";")]
    n=len(idx)
    # unambiguous rows: contain "/" (month-first with time)
    amb=idx[idx.str.contains("/")]
    a=pd.to_datetime(amb,format="%m/%d/%Y %H:%M",errors="coerce")
    out.append((os.path.basename(p),n,len(amb),int(a.isna().sum()),
                str(a.min()),str(a.max())))
for r in out: print("%-32s rows=%7d slash=%7d bad=%d  %s .. %s"%r)
