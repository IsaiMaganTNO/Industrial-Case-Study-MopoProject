import pickle
N=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"))
for k,v in N.items():
  try: print(k, type(v).__name__, getattr(v,"shape",""), list(v.columns)[:12]); print(v.head(3).to_string()[:400])
  except Exception as e: print(k,type(v).__name__)
