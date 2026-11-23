import re,pickle
from collections import Counter
from spinedb_api import DatabaseMapping
def ents(p):
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    return {(e["entity_class_name"],tuple(e["entity_byname"])) for e in m.get_entity_items()}
A=ents(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite")
B=ents(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
pickle.dump((A,B),open(r"run_logs\_red_ents.pkl","wb"))
onlyA=A-B; onlyB=B-A
NBRE=re.compile(r"(BE|NL)C\d")
def tag(e):
  s="__".join(e[1])
  c=sorted(set(re.findall(r"(?<![A-Za-z])(DE|DK|NO|UK)(?![a-z])",s)) | set(re.findall(r"(?:NS|AS|AT|BS)(DE|DK|NO|UK)",s)))
  return ("NB" if NBRE.search(s) else "--")+":"+"+".join(c)
print("onlyA",len(onlyA),Counter((e[0],tag(e)) for e in onlyA).most_common(30))
print("onlyB",len(onlyB));
for k,n in Counter(tag(e) for e in onlyB).most_common(40): print("  ",k,n)
x=[e for e in onlyB if tag(e).endswith(":")];print("onlyB untagged",len(x));[print("   ",e) for e in sorted(x)[:40]]
