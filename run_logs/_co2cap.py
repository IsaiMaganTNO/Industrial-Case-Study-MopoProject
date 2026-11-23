import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu.sqlite")
q="""select e.name,pd.name,substr(cast(pv.value as text),1,250) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like '%CO2-storage%' or e.name like '%CO2-injection%'"""
for r in c.execute(q): print(r)
