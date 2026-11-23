import pandas as pd
T={"DE","DK","NO","UK"}
print("=== GAS: pan-EU vs wired placeholder, per sheet ===")
full=r"data/Gas/Gas_Sectors_Dataset.xlsx"
plc =r"data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"
a=pd.ExcelFile(full); b=pd.ExcelFile(plc)
print("full sheets:", a.sheet_names)
print("plc  sheets:", b.sheet_names)
print("sheet sets equal:", set(a.sheet_names)==set(b.sheet_names))
for s in a.sheet_names:
    da=pd.read_excel(full,s); db=pd.read_excel(plc,s)
    print("  %-14s full_rows=%-4d plc_rows=%-4d cols_equal=%s" % (s,len(da),len(db),list(da.columns)==list(db.columns)))
