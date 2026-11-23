import pandas as pd
F={"NEW_low":r"verification\CO2_data_IC1_low_cost.xlsx","NEW_high":r"verification\CO2_data_IC1_high_cost.xlsx",
   "OLD_low":r"data\CO2_network\CO2_data_IC1_low_cost.xlsx","PIPE":r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"}
X={k:pd.read_excel(v,sheet_name=None) for k,v in F.items()}
for k,v in X.items(): print(k,{s:d.shape for s,d in v.items()})
def cmp(a,b,sheet,keys):
  A=X[a].get(sheet); B=X[b].get(sheet)
  if A is None or B is None: return f"{sheet}: missing in {'a' if A is None else 'b'}"
  m=A.merge(B,on=keys,how="outer",suffixes=("_a","_b"),indicator=True)
  num=[c[:-2] for c in m.columns if c.endswith("_a") and pd.api.types.is_numeric_dtype(m[c])]
  out=[f"{sheet}: rows a={len(A)} b={len(B)} only_a={(m._merge=='left_only').sum()} only_b={(m._merge=='right_only').sum()}"]
  for c in num:
    d=(m[c+"_a"]-m[c+"_b"]).abs(); n=(d>1e-9).sum()
    if n: r=(m[c+"_a"]/m[c+"_b"]).where(d>1e-9); out.append(f"   {c}: {n} differ, ratio a/b min {r.min():.3f} median {r.median():.3f} max {r.max():.3f}")
  return "\n".join(out)
K={"network":["from","to","mode"],"network_to_storage":["from","to"],"storage":["node","type","year"]}
for a,b in [("PIPE","NEW_low"),("PIPE","NEW_high"),("OLD_low","NEW_low"),("NEW_low","NEW_high")]:
  print(f"\n===== {a} vs {b}")
  for s,k in K.items():
    try: print(cmp(a,b,s,k))
    except Exception as e: print(s,"ERR",e)
