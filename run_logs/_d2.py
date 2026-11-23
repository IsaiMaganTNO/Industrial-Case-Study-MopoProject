import pandas as pd, os, re, collections
B=r"verification\Data - IC1 and PECD1"
def classify(vals):
    vals=[str(v) for v in vals if str(v) not in ("nan","None","")]
    ic1={v for v in vals if re.fullmatch(r"(BE|NL)C\d",v)}
    pecd={v for v in vals if re.fullmatch(r"[A-Z]{2}",v)}
    nuts={v for v in vals if re.fullmatch(r"[A-Z]{2}\d{1,3}",v)}
    off={v for v in vals if re.fullmatch(r"(NS|EM|AS|AT|BL|BS|MS)[A-Z]{2}\d*",v)}
    return ic1,pecd,nuts,off
# potential_wind-on.xlsx : sheets + id column
for f in ["potential_wind-on.xlsx","potential_wind-off-FB.xlsx"]:
    p=os.path.join(B,"VRE","VRE_greenfield_installation_potentials",f)
    xl=pd.ExcelFile(p)
    print(f"\n===== {f}  sheets={xl.sheet_names[:8]} (n={len(xl.sheet_names)})")
    d=xl.parse(xl.sheet_names[0],nrows=5)
    print("  cols:",list(d.columns)[:10])
    print(d.head(3).to_string()[:400])
