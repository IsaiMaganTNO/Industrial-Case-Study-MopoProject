import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu.sqlite")
for r in c.execute("select e.name,pd.name,a.name,substr(cast(pv.value as text),1,160) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where (e.name like 'CO2-injection%' and e.name not like '%\\_\\_%\\_\\_%' escape '\\') or (e.name like 'CO2-storage%' ) order by 1,2"): print(r)
