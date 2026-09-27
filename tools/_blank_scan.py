import pandas as pd
out = open("tools/_blank_out.txt", "w", encoding="utf-8")
def w(*a): print(*a, file=out)

xl = r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx"
sheets = pd.read_excel(xl, sheet_name=None)
w("sheets:", list(sheets))
for name, df in sheets.items():
    if df.empty:
        continue
    key = df.columns[0]
    num = df.select_dtypes("number")
    if num.shape[1] == 0:
        continue
    allblank = df[num.isna().all(axis=1)]
    if len(allblank):
        w(f"\n--- {name}: {len(allblank)} row(s) with ALL numeric cells blank ---")
        for _, r in allblank.iterrows():
            w("   ", r.iat[0])
    partial = df[num.isna().any(axis=1) & ~num.isna().all(axis=1)]
    if len(partial):
        w(f"  ({name}: {len(partial)} row(s) partially blank)")
out.close()
