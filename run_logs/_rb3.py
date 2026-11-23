import pandas as pd, os
T={"DE","DK","NO","UK"}
def probe(p, maxs=6):
    print("\n####", p, os.path.getsize(p))
    try: xl=pd.ExcelFile(p)
    except Exception as e: print("  ERR",e); return
    for s in xl.sheet_names[:maxs]:
        d=pd.read_excel(p,s,nrows=400)
        cols=[str(c) for c in d.columns]
        hits=[c for c in cols if c.strip() in T]
        # also look for a region-ish column holding country codes
        rowhits=set()
        for c in d.columns[:6]:
            vals=set(str(v).strip() for v in d[c].dropna().unique()[:600])
            rowhits |= (vals & T)
        print("  [%s] rows~%d cols=%d | target COLS=%s | target VALUES=%s" % (
            s, len(d), len(cols), hits or "-", sorted(rowhits) or "-"))
        print("      cols:", cols[:10])
for p in [r"data/VRE/Technical_potential_GW_per_industrial_region.xlsx",
          r"data/VRE/Existing_GW_per_industrial_region.xlsx",
          r"data/Hydro/EU_parameters_data_20260215_version1.xlsx",
          r"data/Hydro/IC1_parameters_data.xlsx",
          r"data/Gas/Gas_Sectors_Dataset.xlsx",
          r"data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"]:
    probe(p)
