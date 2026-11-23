import sqlite3,re
def get(p):
  d=sqlite3.connect(p); r={}
  for cid,c,p_,a,v in d.execute("select e.id,(select x.name from entity_element ee join entity x on x.id=ee.element_id where ee.entity_id=e.id and position=0),pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class k on k.id=e.class_id join alternative al on al.id=pv.alternative_id where k.name in ('connection__from_node','connection__to_node','connection__node__node') union all select e.id,e.name,pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class k on k.id=e.class_id join alternative al on al.id=pv.alternative_id where k.name='connection'"):
    r.setdefault(c,[]).append((p_,a,v))
  return {k:sorted(v) for k,v in r.items()}
A=get(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"); B=get(r"checkpoints/Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite")
I=re.compile(r"^((BE|NL)C\d+)_\w+_((BE|NL)C\d+)$")
intra=lambda c:(m:=I.match(c)) and m.group(2)==m.group(4)
print("kept conns w/ params A",sum(1 for c in A if not intra(c)),"B",len(B))
print("diff",[c for c in A if not intra(c) and A[c]!=B.get(c)][:5], [c for c in B if c not in A][:5])
