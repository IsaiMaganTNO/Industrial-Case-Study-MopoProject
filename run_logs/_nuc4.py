import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite")
print(c.execute("pragma integrity_check").fetchone())
print(c.execute("select count(*),sum(cast(pv.value as text)+0) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id where pd.name='investment_count_initial_cumulative' and ec.name='connection'").fetchone())
