import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac.sqlite")
q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,150) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where (e.name like 'nuclear-3_BEC1' or e.name like '%nuclear%' and e.name not like 'nuclear-3_%') and (pd.name like '%max%' or pd.name like '%capacity%' or pd.name like '%count%')"""
for r in c.execute(q): print(r)
for r in c.execute("select e.name, ec.name from entity e join entity_class ec on ec.id=e.class_id where e.name like '%nuclear%' and ec.name not in ('unit','unit__to_node','unit__from_node','node__to_unit','unit__node__node') limit 20"): print(r)
