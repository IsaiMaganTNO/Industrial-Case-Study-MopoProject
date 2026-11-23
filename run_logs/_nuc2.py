import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac.sqlite")
q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,120) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name in ('nuclear-3_BEC1','nuclear-3_NLC1') and pd.name in ('capacity_per_unit','unit_capacity','investment_count_max_cumulative')"""
for r in c.execute(q): print(r)
q="""select e.name,pd.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like 'nuclear-3_BEC1__%' or e.name like 'nuclear-3_BEC1\_\_%' escape '\\' limit 10"""
for r in c.execute(q): print(r)
print(c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'nuclear-3\_%' escape '\\'").fetchone())
