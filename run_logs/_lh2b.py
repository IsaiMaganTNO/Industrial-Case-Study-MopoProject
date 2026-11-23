import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
print(c.execute("select pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name='global-H2' and pd.name='tax_out_unit_flow'").fetchone()[0])
print(c.execute("select count(*) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like '%LH2%' and (pd.name like 'fix_%' or pd.name like '%min%')").fetchone())
