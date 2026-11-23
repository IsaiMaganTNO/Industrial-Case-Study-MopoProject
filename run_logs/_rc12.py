import pandas as pd
n=368184
idx=pd.date_range("1980-01-01 00:00",periods=n,freq="h")
print("reconstructed:",idx[0],"->",idx[-1],"n",len(idx))
print("expected end 2021-12-31 23:00 :", idx[-1]==pd.Timestamp("2021-12-31 23:00"))
# verify against unambiguous slash rows of a SP199 file
p=r"data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
s=pd.read_csv(p,index_col=0,usecols=[0],low_memory=False)
raw=pd.Series(s.index.astype(str))
raw=raw[~raw.str.startswith(";")].reset_index(drop=True)
assert len(raw)==n, len(raw)
m=raw.str.contains("/")
parsed=pd.to_datetime(raw[m],format="%m/%d/%Y %H:%M")
print("slash rows:",m.sum(),"| mismatches vs reconstruction:",int((parsed.values!=idx[m.values]).sum()))
# verify date-only rows agree on the DATE (dayfirst)
d=pd.to_datetime(raw[~m],format="%d-%m-%Y")
print("dash rows:",(~m).sum(),"| date mismatches:",int((d.dt.date.values!=pd.Series(idx[~m.values]).dt.date.values).sum()))
