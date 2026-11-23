import sqlite3
for db in [r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu.sqlite"]:
    c=sqlite3.connect(db)
    print(c.execute("select e.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='balance_penalty'").fetchall()[:20])
