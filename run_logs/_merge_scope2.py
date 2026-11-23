import sqlite3,re,collections
db=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
q=lambda s,*a:db.execute(s,a).fetchall()
pat=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_(BE|NL)C\d+$")
nodes={r[0]:r[1] for r in q("select e.name,e.id from entity e join entity_class c on c.id=e.class_id where c.name='node'") if pat.match(r[0])}
print(len(nodes))
ids=set(nodes.values())
cnt=collections.Counter()
for cls,eid in q("select c.name,ee.entity_id from entity_element ee join entity e on e.id=ee.entity_id join entity_class c on c.id=e.class_id where ee.element_id in (%s)"%",".join(map(str,ids))): cnt[cls]+=1
print(cnt)
for n,v in q("select e.name,pd.name from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.id in (%s)"%",".join(map(str,ids))):
  cnt2=1
pc=collections.Counter((re.sub(r'_(BE|NL)C\d+','',n),p) for n,p in q("select e.name,pd.name from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.id in (%s)"%",".join(map(str,ids))))
for k,v in sorted(pc.items()): print(k,v)
