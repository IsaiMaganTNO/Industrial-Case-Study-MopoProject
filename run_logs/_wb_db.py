import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac.sqlite")
for r in c.execute("select a.name,count(*) from parameter_value pv join alternative a on a.id=pv.alternative_id where a.name like 'flex%' or a.name like 'limited%' or a.name like '%refin%' group by a.name"): print(r)
q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,160) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id join entity_class ec on ec.id=e.class_id where ec.name='investment_group'"""
for r in c.execute(q): print(r)
