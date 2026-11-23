import sqlite3,os
c=sqlite3.connect(r"checkpoints\Investment_Results.3day_nb_ccslow_ccu.sqlite")
print([r for r in c.execute("select ec.name, pd.name, count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity_class ec on ec.id=pv.entity_class_id group by 1,2")])
