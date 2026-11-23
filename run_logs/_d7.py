import pandas as pd, re
NEW=r"verification\Data - IC1 and PECD1\Gas\Gas_Sectors_Dataset.xlsx"
NAT=r"data\Gas\Gas_Sectors_Dataset.xlsx"
n=pd.read_excel(NEW,sheet_name="CH4_Production")
nat=pd.read_excel(NAT,sheet_name="CH4_Production")
cap="Capacity 2030 (GWh/d) "
n["reg"]=n["To Country"].astype(str).str.strip()
n["kind"]=n.reg.map(lambda x:"IC1" if re.fullmatch(r"(BE|NL)C\d",x) else ("PECD1" if re.fullmatch(r"[A-Z]{2}",x) else "?"))
print("rows by kind:"); print(n.kind.value_counts().to_string())
print("\ndoes NEW contain bare BE/NL rows?", sorted(set(n[n.kind=="PECD1"].reg) & {"BE","NL"}))
print("\n--- IC1 aggregate vs national, by technology ---")
ic=n[n.kind=="IC1"].copy(); ic["ctry"]=ic.reg.str[:2]
agg=ic.groupby(["technology","ctry"])[cap].sum()
nat2=nat.copy(); nat2["reg"]=nat2["To Country"].astype(str).str.strip()
natbn=nat2[nat2.reg.isin(["BE","NL"])].groupby(["technology","reg"])[cap].sum()
cmp=pd.concat([agg.rename("IC1_sum"),natbn.rename("national")],axis=1)
cmp["ratio"]=cmp.IC1_sum/cmp.national
print(cmp.round(4).to_string())
