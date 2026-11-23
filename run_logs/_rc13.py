import pandas as pd
n=368184
idx=pd.date_range("1980-01-01 00:00",periods=n,freq="h")
p=r"data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
s=pd.read_csv(p,index_col=0,usecols=[0],low_memory=False)
raw=pd.Series(s.index.astype(str)); raw=raw[~raw.str.startswith(";")].reset_index(drop=True)
m=raw.str.contains("/")
for fmt,lab in [("%d-%m-%Y","DAY-first"),("%m-%d-%Y","MONTH-first")]:
    d=pd.to_datetime(raw[~m],format=fmt,errors="coerce")
    bad=int((d.dt.date.values!=pd.Series(idx[~m.values]).dt.date.values).sum())
    print("%-12s NaT=%-6d date mismatches vs row-order=%d" % (lab,int(d.isna().sum()),bad))
print()
print("first dash rows :", list(raw[~m][:3]), "-> row-order", [str(x) for x in idx[~m.values][:3]])
print("rows 744..746   :", list(raw[744:747]), "-> row-order", [str(x) for x in idx[744:747]])
