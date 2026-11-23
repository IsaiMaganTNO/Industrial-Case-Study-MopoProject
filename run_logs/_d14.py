import pandas as pd
p=r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
xl=pd.ExcelFile(p)
need=["PECD2_IC1","IC1_PECD2","PECD1_IC1","IC1_PECD1","IC1_NUTS3","NUTS3_IC1","OFF3_map"]
print("present sheets relevant:",[s for s in xl.sheet_names if "IC1" in s or "OFF3_map"==s])
for n in need:
    print(f"  {n:12} {'PRESENT' if n in xl.sheet_names else '*** MISSING ***'}")
m=xl.parse("OFF3_map")
print("\nOFF3_map IC1 col non-null:",m["IC1"].notna().sum(),"of",len(m))
print(m[m.IC1.notna()][["source","PECD1","IC1"]].head(20).to_string())
