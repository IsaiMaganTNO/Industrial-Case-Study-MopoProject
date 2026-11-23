import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
p=os.path.join(B,"Rdemand","other_electricity_demand.csv")
d=pd.read_csv(p,nrows=3)
print("=== Rdemand cols (first 25):",list(d.columns)[:25])
print("  ncols:",len(d.columns))
cols=[c for c in d.columns]
ic1=[c for c in cols if re.fullmatch(r"(BE|NL)C\d",str(c))]
p1=[c for c in cols if re.fullmatch(r"[A-Z]{2}",str(c))]
p2=[c for c in cols if re.fullmatch(r"[A-Z]{2}\d{2}",str(c))]
print(f"  IC1 cols={len(ic1)} {ic1}")
print(f"  PECD1 cols={len(p1)} {p1[:20]}")
print(f"  PECD2 cols={len(p2)}")
print("\n=== Buildings scenario demands ===")
d2=pd.read_csv(os.path.join(B,"Buildings","scenario_total_yearly_demands_GWh.csv"),nrows=5)
print("  cols:",list(d2.columns)[:14]); print(d2.head(3).to_string()[:400])
