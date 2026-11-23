import sqlite3
db=sqlite3.connect(r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
for r in db.execute("select e.name,pd.name,a.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name like 'wind-off%NSBE%' and (pd.name like '%max%' or pd.name like '%existing%' or pd.name like '%initial%')"): print(r)
