import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap125.sqlite")
for r in c.execute("select e.name,pd.name,a.name,substr(cast(pv.value as text),1,120) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name like 'DAC\\_NLC1%' escape '\\' and pd.name not like 'lifetime%'"): print(r)
print("existing_units def:",c.execute("select default_value from parameter_definition where name='existing_units'").fetchone())
