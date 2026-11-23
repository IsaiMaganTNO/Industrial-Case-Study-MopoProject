import sqlite3,re,collections
db=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
q=lambda s,*a:db.execute(s,a).fetchall()
pat=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_(BE|NL)C\d+$")
N={r[0]:r[1] for r in q("select e.name,e.id from entity e join entity_class c on c.id=e.class_id where c.name='node'") if pat.match(r[0])}
ctry=lambda n:re.sub(r'C\d+$','',n)
ids=",".join(map(str,N.values()))
print(q("select e.name,a.name,pv.type,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name='storage_active' and e.id in (%s) limit 3"%ids))
print("ntb",collections.Counter(re.sub(r'_(BE|NL)C\d+','',r[0]) for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='node__temporal_block' and e.id in (select entity_id from entity_element where element_id in (%s))"%ids)))
print(q("select distinct pd.name, pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id where c.name='node__temporal_block' limit 10"))
# duplicates: unit/connection hitting >1 zone node of same country carrier
for cls in ['unit__to_node','node__to_unit','connection__from_node','connection__to_node']:
  rows=q("select e.id,(select group_concat(x.name,'|') from entity_element ee join entity x on x.id=ee.element_id where ee.entity_id=e.id order by ee.position) from entity e join entity_class c on c.id=e.class_id where c.name=?",cls)
  keys=collections.Counter()
  for i,nm in rows:
    parts=nm.split('|'); parts=[ctry(p) if p in N else p for p in parts]; keys[tuple(parts)]+=1
  print(cls,sum(v-1 for v in keys.values() if v>1))
# unit_flow__unit_flow dims
print(q("select c.name,c.dimension_count from entity_class c where c.name like 'unit_flow%' or c.name like 'connection__node__node'"))
print(q("select dc.name from entity_class_dimension d join entity_class c on c.id=d.entity_class_id join entity_class dc on dc.id=d.dimension_id where c.name='unit_flow__unit_flow' order by d.position"))
