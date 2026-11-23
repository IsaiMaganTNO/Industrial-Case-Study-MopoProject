import pandas as pd, os
src=r"data/Rdemand/other_electricity_demand.csv"
ref=r"data/Rdemand/other_electricity_demand_IC1.csv"
dst=r"data/Rdemand/other_electricity_demand_IC1_NWEU.csv"
KEEP=["BEC%d"%i for i in range(1,9)]+["NLC%d"%i for i in range(1,10)]+["DE","DK","NO","UK"]
d=pd.read_csv(src, sep=";", index_col=0)
d.index=pd.to_datetime(d.index, dayfirst=True)
print("source:", d.shape, "range", d.index.min(), "->", d.index.max())
missing=[c for c in KEEP if c not in d.columns]
assert not missing, missing
out=d[KEEP].copy()
# sanity vs the currently-wired IC1 file
r=pd.read_csv(ref, index_col=0)
r.index=pd.to_datetime(r.index)
r=r.loc[:, [c for c in r.columns if not str(c).startswith("Unnamed")]]
common=out.index.intersection(r.index)
print("overlap hours:", len(common))
diff=(out.loc[common, [c for c in KEEP if c in r.columns]] - r.loc[common, [c for c in KEEP if c in r.columns]]).abs().max().max()
print("max |diff| vs wired IC1 file on shared cols:", diff)
out.to_csv(dst, index_label="")
print("written", dst, os.path.getsize(dst))
chk=pd.read_csv(dst, parse_dates=True, index_col=0)   # default comma, as demand_DB.py does
print("VERIFY default-comma parse -> ncols:", len(chk.columns), list(chk.columns))
print("   index[:2]:", list(chk.index[:2]), "| dtype", chk.index.dtype)
print("   2009 hours present:", int((chk.index.year==2009).sum()))
print("   NaNs:", int(chk.isna().sum().sum()))
print("\n2009 annual TWh:")
print((chk[chk.index.year==2009].sum()/1e6).round(1).to_string())
