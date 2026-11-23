import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
NB={"BE","NL"}
def show(t,v):
    v=[str(x).strip() for x in v if str(x).strip() not in ("nan","None","")]
    ic1={x for x in v if re.fullmatch(r"(BE|NL)C\d",x)}
    p1={x for x in v if re.fullmatch(r"[A-Z]{2}",x)}
    p2={x for x in v if re.fullmatch(r"[A-Z]{2}\d{2}",x)}
    n3={x for x in v if re.fullmatch(r"[A-Z]{2}\d{3}",x)}
    print(f"  {t[:44]:46} IC1={len(ic1):3} PECD1={len(p1):3} PECD2={len(p2):4} NUTS3={len(n3):4} nonBENL_P1={len(p1-NB):3}")
print("=== Industry ===")
for f in ["technology_catalogue_ind_nuts0_nuts3_update.xlsx","production_JRC_IDEES_nuts3.xlsx"]:
    p=os.path.join(B,"Industry",f); xl=pd.ExcelFile(p)
    print(f" {f} sheets({len(xl.sheet_names)}):",xl.sheet_names[:9])
    for s in xl.sheet_names[:5]:
        d=xl.parse(s,nrows=4000)
        allv=pd.concat([d[c].astype(str) for c in d.columns])
        show(f"  {s} {d.shape}",allv)
print("\n=== Energy_Conversion powerplants (head) ===")
d=pd.read_csv(os.path.join(B,"Energy_Conversion","powerplants.csv"),nrows=5)
print("  cols:",list(d.columns)[:14])
print(d.head(3).to_string()[:400])
