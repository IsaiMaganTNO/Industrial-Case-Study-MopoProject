import pickle,numpy as np
from collections import defaultdict
from spinedb_api import from_database
A,B,ex=pickle.load(open(r"run_logs\_cmp_in.pkl","rb"))
SC={"Base","wy2009","medium_bio","current","GA","GA_flex0","high_CO2","flex_buildings","flex_buildings_wy2009_current","flex_industry"}
TY={}
import sqlite3
def typ(p,k):
  pass
from spinedb_api import DatabaseMapping
def types(p):
  t={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for v in m.get_parameter_value_items():
      t[(v["entity_class_name"],"__".join(v["entity_byname"]),v["parameter_definition_name"],v["alternative_name"])]=v["type"]
  return t
tA=types(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite")
tB=types(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
def arr(b,t):
  x=from_database(b,t)
  if hasattr(x,"values"):
    try: return np.array([float(getattr(y,"value",y)) for y in x.values]),list(map(str,getattr(x,"indexes",[])))
    except: return None,None
  try: return np.array([float(x)]),[]
  except: return None,None
st=defaultdict(list)
for k in ex:
  if k[3] not in SC: continue
  a,ia=arr(A[k],tA[k]); b,ib=arr(B[k],tB[k])
  if a is None or b is None: st[k[2]].append((k[1],"nonnum")); continue
  if len(a)!=len(b): st[k[2]].append((k[1],f"len {len(a)}->{len(b)}", ia[:4], ib[:4])); continue
  r=np.nanmax(np.abs(b-a)/np.maximum(np.abs(a),1e-9)); st[k[2]].append((k[1],round(float(r),4),a[:4].round(4).tolist(),b[:4].round(4).tolist()))
for p,l in st.items():
  print(f"== {p} n={len(l)}")
  for x in l[:4]: print("   ",x)
