import pandas as pd
p=r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
ic1=pd.read_excel(p,sheet_name="IC1")
print("IC1 ids:", list(ic1.id))
print("IC1 countries:", sorted(set(ic1.country)))
t=pd.read_excel(p,sheet_name="PECD1_IC1")
print("PECD1_IC1 rows:",len(t))
ident=t[t.source==t.target]
print("identity rows:",len(ident), list(ident.source))
nonid=t[t.source!=t.target]
print("non-identity rows:",len(nonid))
print(nonid.to_string())
