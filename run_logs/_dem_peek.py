import sqlite3, json
c=sqlite3.connect(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\Investment_Results.3day_mr_ccslow_ccu_cap16_dac0.sqlite")
q="""select e.name, ec.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id where pd.name='demand' limit 3"""
for r in c.execute(q): print(r[0], r[1], r[2][:150])
print(c.execute("select count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='demand'").fetchone())
