import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
q="""select e.name,pd.name,a.name,substr(pv.value,1,200) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name like '%CO2-storage-DK%' or e.name like '%CO2-injection-DK%'"""
for r in c.execute(q): print(r)
