import sqlite3
M = r"checkpoints\frlu\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
c = sqlite3.connect(M)
for e, p, t in c.execute("""select e.name, pd.name, substr(cast(pv.value as text),1,140) from parameter_value pv join entity e on e.id=pv.entity_id
  join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like 'nuclear-3-existing_%' and pd.name in ('investment_count_max_cumulative','capacity_per_unit','lifetime_technical')"""):
    print(e, p, t)
for e, t in c.execute("""select e.name, substr(cast(pv.value as text),1,100) from parameter_value pv join entity e on e.id=pv.entity_id
  join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='capacity_per_unit' and e.name like '%nuclear-3-existing_%'"""):
    print(e, t)
