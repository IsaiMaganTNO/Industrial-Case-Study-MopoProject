import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
def rpt(name, vals):
    vals=[str(v) for v in vals if str(v)!="nan"]
    ic1=sorted({v for v in vals if re.fullmatch(r"(BE|NL)C\d",v)})
    pecd=sorted({v for v in vals if re.fullmatch(r"[A-Z]{2}",v)})
    off=sorted({v for v in vals if re.fullmatch(r"[A-Z]{2}[A-Z]{2}\d*",v) and v[:2] in ("NS","EM","AS","AT","BL","BS","MS")})
    print(f"\n### {name}")
    print(f"  IC1 ({len(ic1)}): {ic1}")
    print(f"  PECD1 ({len(pecd)}): {pecd}")
    if off: print(f"  OFF ({len(off)}): {off[:14]}")
# VRE potentials
for f in ["Technical_potential_GW_per_industrial_region.xlsx","Existing_GW_per_industrial_region.xlsx"]:
    p=os.path.join(B,"VRE",f)
    xl=pd.ExcelFile(p)
    print(f"\n===== {f} sheets={xl.sheet_names}")
    d=xl.parse(xl.sheet_names[0])
    print("  cols:",list(d.columns)[:12], "rows",len(d))
    print(d.head(4).to_string()[:500])
