import pandas as pd, os, re
NEW=r"verification\Data - IC1 and PECD1\Gas\Gas_Sectors_Dataset.xlsx"
OLD=r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx"
NAT=r"data\Gas\Gas_Sectors_Dataset.xlsx"
import hashlib
for t,p in [("NEW(verification)",NEW),("OLD IC1 placeholder",OLD),("national",NAT)]:
    if not os.path.exists(p): print(t,"MISSING"); continue
    h=hashlib.md5(open(p,"rb").read()).hexdigest()[:10]
    d=pd.read_excel(p,sheet_name="CH4_Production")
    print(f"\n== {t}  md5={h}  shape={d.shape}")
    print("  cols:",list(d.columns))
    print(d.head(6).to_string()[:600])
