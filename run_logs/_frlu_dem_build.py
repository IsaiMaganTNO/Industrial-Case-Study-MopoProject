import pandas as pd, os
src=r"data/Rdemand/other_electricity_demand.csv"
ref=r"data/Rdemand/other_electricity_demand_IC1_NWEU.csv"
dst=r"data/Rdemand/other_electricity_demand_IC1_NWEU_FRLU.csv"
KEEP=["BEC%d"%i for i in range(1,9)]+["NLC%d"%i for i in range(1,10)]+["DE","DK","NO","UK","FR","LU"]
d=pd.read_csv(src, sep=";", index_col=0); d.index=pd.to_datetime(d.index, dayfirst=True)
out=d[KEEP].copy()
r=pd.read_csv(ref, index_col=0, parse_dates=True)
com=out.index.intersection(r.index)
print("max|diff| vs 21-region file on its 21 cols:", (out.loc[com, r.columns]-r.loc[com]).abs().max().max(), "rows", len(out), len(r))
out.to_csv(dst, index_label="")
chk=pd.read_csv(dst, parse_dates=True, index_col=0)
print("cols", len(chk.columns), list(chk.columns)[-6:], "NaNs", int(chk.isna().sum().sum()))
print((chk[chk.index.year==2009].sum()/1e6).round(1)[["DE","UK","FR","LU","NLC1"]].to_string())
