import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
q="""select e.name,pd.name,a.name,substr(pv.value,1,160) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where (e.name like 'CO2-storage-%') and pd.name like 'storage_%' and pd.name not in ('storage_active','storage_longterm_active') order by e.name"""
for r in c.execute(q): print(r)
r=sqlite3.connect(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
print([x for x in r.execute("select distinct pd.name from parameter_definition pd") if 'storage' in x[0]])
