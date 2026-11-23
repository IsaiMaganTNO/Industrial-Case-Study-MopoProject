import pandas as pd,glob
for f in glob.glob(r"data\**\*.xlsx",recursive=True):
    try: xs=pd.ExcelFile(f)
    except Exception: continue
    for s in xs.sheet_names:
        if "co2" in s.lower() or "fuel" in s.lower() or "commodit" in s.lower():
            print(f.split("\\")[-1][:42],"|",s)
