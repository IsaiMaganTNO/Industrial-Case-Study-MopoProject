import pandas as pd
out = open("tools/_tc_out.txt", "w", encoding="utf-8")
def w(*a): print(*a, file=out)
df = pd.read_excel(r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx", sheet_name="Technology_Costs")
w("cols:")
for i, c in enumerate(df.columns):
    w(f"  [{i}] {c}")
num = df.select_dtypes("number")
mask = num.isna().any(axis=1)
w(f"\n{int(mask.sum())} partially-blank rows:")
for idx in df[mask].index:
    r = df.loc[idx]
    miss = [c for c in num.columns if pd.isna(r[c])]
    w(f"\n  {r.iat[0]}")
    w(f"    missing: {miss}")
out.close()
