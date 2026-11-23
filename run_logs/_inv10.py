import os,re,sys,collections
sys.path.insert(0,"tools")
from spinedb_api import DatabaseMapping, from_database
I=re.compile(r"^((BE|NL)C\d+)_(elec|H2|CH4)_((BE|NL)C\d+)$")
res=r"runs\3day_nb_v2\output\Investment_Results.3day_nb_v2.sqlite"
inv=collections.Counter(); flows=collections.defaultdict(list)
def leaf(x):
  while hasattr(x,"values") and len(x.values) and hasattr(x.values[0],"values"): x=x.values[-1]
  return x
with DatabaseMapping("sqlite:///"+os.path.abspath(res)) as db:
  for v in db.get_parameter_value_items(entity_class_name="report__connection__stochastic_scenario"):
    c=v["entity_byname"][1]; m=I.match(c)
    if m and m.group(2)==m.group(5) and v["parameter_definition_name"]=="connections_invested":
      val=from_database(v["value"],v["type"]); s=sum(float(x) for x in val.values)
      if s>1e-6: inv[(m.group(3),c)]+=s
  for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario",parameter_definition_name="connection_flow"):
    bn=v["entity_byname"]; m=I.match(bn[1])
    if m and m.group(2)==m.group(5) and bn[3]=="to_node":
      val=from_database(v["value"],v["type"]); xs=[float(x) for x in val.values]
      flows[(m.group(3),bn[1])]=xs
print("SA intra connections invested (sum over years):",len(inv)); 
for k,s in sorted(inv.items(),key=lambda z:-z[1])[:15]: print("  ",k,round(s,3))
print("connections with >=20% of hours at their own peak (proxy for binding limit):")
cnt=collections.Counter()
for (car,c),xs in flows.items():
  mx=max(xs) if xs else 0
  if mx<1e-3: continue
  sh=sum(x>=0.99*mx for x in xs)/len(xs)
  if sh>=0.2: cnt[car]+=1
print(" ",dict(cnt),"of",collections.Counter(k[0] for k in flows))
