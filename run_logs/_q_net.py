import sqlite3,re,collections,json
d=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
Q="""select c.name,e.name,pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id"""
R=d.execute(Q).fetchall()
Z=re.compile(r"^((BE|NL)C\d+)_(elec|H2|CH4)_((BE|NL)C\d+)")
conns=collections.defaultdict(set)
for c,e,p,a,v in d.execute("select c.name,e.name,'','','' from entity e join entity_class c on c.id=e.class_id where c.name='connection'"):
  m=Z.match(e)
  if m: conns[m.group(3)].add(e)
for car in ["elec","H2","CH4"]:
  cs=conns[car]; pc=collections.defaultdict(set)
  for c,e,p,a,v in R:
    head=e.split("__")[0]
    if head in cs: pc[(c,p)].add(head)
  print(f"== {car}: {len(cs)} connections between zones")
  for k,s in sorted(pc.items()): print(f"   {k[0]:24s} {k[1]:40s} on {len(s)}")
# examples
for car,ex in [("elec","NLC3_elec_NLC4"),("H2","NLC2_H2_NLC3"),("CH4","NLC2_CH4_NLC3")]:
  print("--",ex)
  for c,e,p,a,v in R:
    if e.split("__")[0]==ex: print(f"   {p:40s} {a:8s} {v[:110]!r}")
print("== salt cavern / H2 storage params")
for c,e,p,a,v in R:
  if "salt-cavern_NLC2" in e: print(f"   {c:22s} {e[:45]:45s} {p:42s} {v[:90]!r}")
