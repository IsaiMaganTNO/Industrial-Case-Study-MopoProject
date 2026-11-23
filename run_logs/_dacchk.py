import sqlite3,sys
for db in sys.argv[1:]:
    c=sqlite3.connect(db)
    print(db)
    for r in c.execute("select pd.name,count(*),min(cast(pv.value as text)),max(cast(pv.value as text)) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like 'DAC\\_%' escape '\\' and e.name not like '%\\_\\_%' escape '\\' group by 1",): print("  ",r)
    print("  units:",c.execute("select count(*) from entity where name like 'DAC\\_%' escape '\\' and name not like '%\\_\\_%' escape '\\'").fetchone())
