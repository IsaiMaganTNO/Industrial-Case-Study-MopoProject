import sqlite3,re,collections,json
db=sqlite3.connect(r"runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
q=lambda s,*a:db.execute(s,a).fetchall()
pat=re.compile(r"^(elec|CH4|H2|CO2|HC|MeOH|bio)_(BE|NL)C\d+$")
N={r[1]:r[0] for r in q("select e.name,e.id from entity e join entity_class c on c.id=e.class_id where c.name='node'") if pat.match(r[0])}
ids=",".join(map(str,N))
print([r[0] for r in q("select name from sqlite_master where type='table'")])
print("groups",q("select count(*) from entity_group where entity_id in (%s) or member_id in (%s)"%(ids,ids)))
print("ent_alt",q("select count(*) from entity_alternative where entity_id in (%s)"%ids))
r=q("select e.name,a.name,pv.type,substr(pv.value,1,200) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name='demand' and e.id in (%s)"%ids)
print(collections.Counter((x[1],x[2]) for x in r)); print(r[0])
v=collections.Counter((a,t,v) for _,a,t,v in [(x[0],*x[1:]) for x in []])
p=q("select pd.name,a.name,pv.type,pv.value,count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id where c.name='node__temporal_block' and e.id in (select entity_id from entity_element where element_id in (%s)) group by 1,2,3,4"%ids)
print(p)
