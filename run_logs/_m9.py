import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
T={"NO","DE","DK","UK"}
d=pd.read_csv(os.path.join(B,"VRE","VRE_time_series","wind-on-SP277-HH100.csv"),nrows=3)
cols=[str(c) for c in d.columns]
for cc in sorted(T):
    sub=[c for c in cols if c.startswith(cc) and c!="time"]
    print(f"  {cc}: {len(sub)} PECD2 regions -> {sub}")
print("\nIC1 cols:",[c for c in cols if re.fullmatch(r'(BE|NL)C\d',c)][:4],"...")
# transformer availability for PECD2->PECD1
import pandas as pd
xl=pd.ExcelFile(r"data-pipelines\europe\_ines-builder\region_transformation.xlsx")
t=xl.parse("PECD2_PECD1")
print("\nPECD2_PECD1 sheet rows:",len(t),"cols:",list(t.columns))
sub=t[t.target.isin(T)]
print("  rows for NO/DE/DK/UK:",len(sub))
print(sub.groupby("target").size().to_string())
