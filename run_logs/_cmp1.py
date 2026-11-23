import re,sys
from collections import Counter
from spinedb_api import DatabaseMapping,from_database
def load(p):
  d={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for v in m.get_parameter_value_items():
      e="__".join(v["entity_byname"])
      if not re.search(r"(BE|NL)C\d|^atmosphere|^fossil-CH4|^global|NSNL|NSBE|^nuclear-3_(BE|NL)$",e): continue
      d[(v["entity_class_name"],e,v["parameter_definition_name"],v["alternative_name"])]=bytes(v["value"]) if v["value"] is not None else None
  return d
A=load(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite")
B=load(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
onlyA=Counter(k[2] for k in A.keys()-B.keys()); onlyB=Counter(k[2] for k in B.keys()-A.keys())
diff=Counter(k[2] for k in A.keys()&B.keys() if A[k]!=B[k])
print("NL+BE keys",len(A),len(B)); print("ONLY nn_fix",dict(onlyA.most_common(15))); print("ONLY mr_fix",dict(onlyB.most_common(15))); print("VALUE DIFF",dict(diff.most_common(20)))
ex=[k for k in A.keys()&B.keys() if A[k]!=B[k]]
for k in ex[:12]:
  try: print(k, from_database(A[k]) if False else "")
  except: pass
import pickle; pickle.dump((A,B,ex),open(r"run_logs\_cmp_in.pkl","wb"))
