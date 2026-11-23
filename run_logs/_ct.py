import sqlite3
c=sqlite3.connect(r'checkpoints\Final_SpineOpt_Model.tiny.3day.nb_cp.sqlite')
print(c.execute("select e.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where pd.name='connection_type'").fetchall())
