import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
NB={"BE","NL"}
def cls(v):
    v=[str(x).strip() for x in v if str(x).strip() not in ("nan","None","")]
    return ({x for x in v if re.fullmatch(r"(BE|NL)C\d",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}\d{2}",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}\d{3}",x)})
def show(t,v):
    a,b,c,d=cls(v)
    print(f"  {t[:44]:46} IC1={len(a):3} PECD1={len(b):3} PECD2={len(c):4} NUTS3={len(d):4} nonBENL_P1={len(b-NB):3}")
# Gas
p=os.path.join(B,"Gas","Gas_Sectors_Dataset.xlsx")
xl=pd.ExcelFile(p); print("=== Gas sheets:",xl.sheet_names)
for s in xl.sheet_names:
    d=xl.parse(s)
    allv=pd.concat([d[c].astype(str) for c in d.columns])
    show(f"{s} ({d.shape})",allv)
# Hydro
p=os.path.join(B,"Hydro","EU_parameters_data_20260215_version1.xlsx")
xl=pd.ExcelFile(p); print("\n=== Hydro sheets:",xl.sheet_names)
for s in xl.sheet_names[:6]:
    d=xl.parse(s); allv=pd.concat([d[c].astype(str) for c in d.columns])
    show(f"{s} ({d.shape})",allv)
