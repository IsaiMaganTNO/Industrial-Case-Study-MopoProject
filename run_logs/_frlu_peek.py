import sqlite3
N = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\output\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(N)
for r in c.execute("""select ec.name, e.name, pd.name, a.name, substr(cast(pv.value as text),1,200) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id
 where pd.name='units_invested_available' limit 3"""): print(r)
