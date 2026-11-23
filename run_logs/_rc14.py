import pandas as pd
for p in [r"data/VRE/VRE_time_series/wind-off-FB-SP316-HH155.csv",
          r"data/VRE/VRE_time_series/wind-off-FB-existing.csv"]:
    s=pd.read_csv(p,index_col=0,usecols=[0],low_memory=False)
    raw=pd.Series(s.index.astype(str)); raw=raw[~raw.str.startswith(";")]
    print(p.split("/")[-1], "rows",len(raw), "| first", list(raw[:2]), "| has slash:", int(raw.str.contains("/").sum()))
