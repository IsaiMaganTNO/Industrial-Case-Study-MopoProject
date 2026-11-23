import sqlite3,re,collections
db=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
q=lambda s,*a:db.execute(s,a).fetchall()
pat=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_(BE|NL)C\d+$")
N={r[0] for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='node'") if pat.match(r[0])}
ctry=lambda n:re.sub(r'C\d+$','',n) if n in N else n
intra=re.compile(r"^(BE|NL)C\d+_\w+_(BE|NL)C\d+$")
def isintra(c):
  m=re.match(r"^((BE|NL)C\d+)_\w+_((BE|NL)C\d+)$",c); return bool(m) and m.group(2)==m.group(4)
for cls in ['connection__from_node','connection__to_node','connection__node__node','unit_flow__unit_flow','node__temporal_block']:
  rows=q("select e.id,(select group_concat(name,'|') from (select x.name from entity_element ee join entity x on x.id=ee.element_id where ee.entity_id=e.id order by ee.position)) from entity e join entity_class c on c.id=e.class_id where c.name=?",cls)
  keys=collections.Counter(); ex=None
  for i,nm in rows:
    p=nm.split('|')
    if cls.startswith('connection') and isintra(p[0]): continue
    k=tuple(ctry(x) for x in p); keys[k]+=1
    if keys[k]>1: ex=k
  print(cls,len(rows),sum(v-1 for v in keys.values() if v>1),ex)
print(q("select dc.name from entity_class_dimension d join entity_class c on c.id=d.entity_class_id join entity_class dc on dc.id=d.dimension_id where c.name='unit_flow__unit_flow' order by d.position"))
print(q("select count(*) from entity e join entity_class c on c.id=e.class_id where c.name='connection'"), sum(isintra(r[0]) for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='connection'")))
