import pandas as pd, os
B=r"verification\Data - IC1 and PECD1"
xl=pd.ExcelFile(os.path.join(B,"Gas","Gas_Sectors_Dataset.xlsx"))
for s in ["CH4_Storage","H2_Production","H2_Storage","H2_Network"]:
    d=xl.parse(s)
    print(f"\n=== {s}  cols={list(d.columns)[:6]}")
    kc=[c for c in d.columns if d[c].astype(str).str.fullmatch(r"[A-Z]{2}|(BE|NL)C\d").any()]
    for c in kc[:3]:
        print(f"   {c}: {sorted(set(d[c].astype(str).str.strip()))}")
