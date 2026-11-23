import pandas as pd
pd.set_option("display.width",200); pd.set_option("display.max_colwidth",160)
d=pd.read_excel(r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx","CH4_Production")
print(d.shape, list(d.columns))
for t in d.technology.unique():
    s=d[d.technology==t]
    r=s.iloc[0]
    print("="*100)
    print("TECH:",t," rows:",len(s)," regions:",sorted(s["To Country"].unique()))
    for c in d.columns:
        print(f"   {c!s:30s} = {r[c]!s:.160}")
