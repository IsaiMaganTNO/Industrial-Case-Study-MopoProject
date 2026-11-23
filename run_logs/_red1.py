import re
from collections import Counter,defaultdict
from spinedb_api import DatabaseMapping
TOK=re.compile(r"(?:^|[_\-])(DE|DK|NO|UK|FR|LU)(?:$|[_\-])|^(?:CO2-storage-|CO2-injection-|wind-off.*_)?(?:NS|AS|AT|BS|MS)(DE|DK|NO|UK|FR)\d")
def scan(p):
  out=defaultdict(set);cls=Counter()
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for e in m.get_entity_items():
      hit=set()
      for part in e["entity_byname"]:
        for mm in TOK.finditer(part): hit.add(mm.group(1) or mm.group(2))
      if hit:
        k="+".join(sorted(hit)); out[k].add((e["entity_class_name"],"__".join(e["entity_byname"]))); cls[(k,e["entity_class_name"])]+=1
  return out,cls
A,ca=scan(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite")
B,cb=scan(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
print("nn_fix:",{k:len(v) for k,v in A.items()});print("mr_fix:",{k:len(v) for k,v in B.items()})
for c in ["FR","LU"]: print(c,"same set:",A.get(c,set())==B.get(c,set()), len(A.get(c,set())-B.get(c,set())), len(B.get(c,set())-A.get(c,set())))
for c in ["DE","DK","NO","UK"]:
  a=A.get(c,set());b=B.get(c,set());print(c,"nn",len(a),"mr",len(b),"nn-not-in-mr",len(a-b))
  print("   ex nn-only",sorted(a-b)[:6])
print(sorted({k for k in A if "+" in k}),sorted({k for k in B if "+" in k})[:10])
# names of all offshore / storage zones
with DatabaseMapping("sqlite:///checkpoints/Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite") as m:
  z=sorted({n for e in m.get_entity_items(entity_class_name="node") for n in [e["name"]] if re.match(r"^(CO2-storage|elec_|CH4_|H2_).*(NS|AS|AT|BS)",n)})
  print("zone nodes",z[:40])
  print("classes",sorted({e["entity_class_name"] for e in m.get_entity_items()}))
