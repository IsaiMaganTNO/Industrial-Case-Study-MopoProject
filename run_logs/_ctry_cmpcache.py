import pickle
a=pickle.load(open(r"run_logs\nb_v2.pkl","rb")); b=pickle.load(open(r"run_logs\nb_ctry.pkl","rb"))
for k in a:
  if hasattr(a[k],"shape"): print(f"{k:10s} {str(a[k].shape):14s} {str(b[k].shape):14s}", list(a[k].columns) if hasattr(a[k],"columns") else "")
for k in ["inv","prod","co2store","co2pipe","supply"]:
  for c in ["region","country"]:
    if c in a[k]: print(k,c,sorted(a[k][c].astype(str).unique())[:20],"|",sorted(b[k][c].astype(str).unique())[:20])
print(a["co2net"].head()); print(a["co2pipe"]); print(b["co2pipe"])
