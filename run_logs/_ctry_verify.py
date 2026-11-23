import sqlite3,re,collections,json
A=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
B=sqlite3.connect(r"checkpoints/Final_SpineOpt_Model.tiny.3day.nb_ctry.sqlite")
def ent(d): return collections.Counter(r[0] for r in d.execute("select c.name from entity e join entity_class c on c.id=e.class_id"))
ea,eb=ent(A),ent(B)
for k in sorted(set(ea)|set(eb)):
  if ea[k]!=eb[k]: print(f"{k:35s}{ea[k]:8d}{eb[k]:8d}{eb[k]-ea[k]:8d}")
def par(d):
  out=collections.defaultdict(lambda:[0,0.0])
  for c,p,a,t,v in d.execute("select c.name,pd.name,al.name,pv.type,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id"):
    o=out[(c,p)]; o[0]+=1
    try:
      x=json.loads(v)
      if isinstance(x,(int,float)): o[1]+=x
      elif isinstance(x,dict) and 'data' in x and isinstance(x['data'],list): o[1]+=sum(y for y in x['data'] if isinstance(y,(int,float)))
    except Exception: pass
  return out
pa,pb=par(A),par(B)
print("--- param diffs (count / numeric sum)")
for k in sorted(set(pa)|set(pb)):
  a,b=pa.get(k,[0,0]),pb.get(k,[0,0])
  if a[0]!=b[0] or abs(a[1]-b[1])>1e-6*max(1,abs(a[1])): print(k,a,b)
N=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_(BE|NL)C\d+$")
print("zone net nodes left",sum(1 for (n,) in B.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='node'") if N.match(n)))
print("country nodes",[n for (n,) in B.execute("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='node' and e.name glob '*_[BN][EL]'")])
for t in ['scenario','alternative','scenario_alternative']: print(t,A.execute(f"select count(*) from {t}").fetchone(),B.execute(f"select count(*) from {t}").fetchone())
