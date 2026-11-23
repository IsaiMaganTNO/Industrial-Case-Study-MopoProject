import pandas as pd, glob, os
for f in glob.glob(r"verification\**\*.xlsx",recursive=True):
    print("#"*100); print(os.path.basename(f))
    xl=pd.ExcelFile(f)
    for s in xl.sheet_names:
        d=xl.parse(s)
        print(f"  [{s}] shape={d.shape} cols={list(d.columns)[:10]}")
