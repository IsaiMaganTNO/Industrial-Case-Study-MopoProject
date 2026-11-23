import re,pickle
from collections import Counter,defaultdict
from spinedb_api import DatabaseMapping,from_database
NB=re.compile(r"(BE|NL)C\d|NSNL|NSBE")
def vals(p):
  d={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for v in m.get_parameter_value_items():
      d[(v["entity_class_name"],tuple(v["entity_byname"]),v["parameter_definition_name"],v["alternative_name"])]=(v["type"],bytes(v["value"]) if v["value"] is not None else None)
  return d
A=vals(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite")
B=vals(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
pickle.dump((A,B),open(r"run_logs\_red_vals.pkl","wb"))
EA,EB=pickle.load(open(r"run_logs\_red_ents.pkl","rb"))
shared_glob={e for e in EA&EB if not NB.search("__".join(e[1]))}
print("shared non-regional entities",len(shared_glob),Counter(e[0] for e in shared_glob))
d=defaultdict(list)
for k in set(A)|set(B):
  if (k[0],k[1]) not in shared_glob: continue
  if A.get(k)!=B.get(k): d[(k[0],k[2])].append((k[1],k[3],"A" if k in A else "-","B" if k in B else "-"))
for k,l in sorted(d.items()): print(k,len(l),l[:3])
