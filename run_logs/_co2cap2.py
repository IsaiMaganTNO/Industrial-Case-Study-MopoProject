import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu.sqlite")
print(c.execute("select s.name,group_concat(a.name||':'||sa.rank) from scenario s join scenario_alternative sa on sa.scenario_id=s.id join alternative a on a.id=sa.alternative_id group by s.name").fetchall())
for e,a,v in c.execute("select e.name,a.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name='storage_investment_count_fix_cumulative' and e.name like 'CO2-storage%'"):
    d=json.loads(v)["data"]; print(e,a,{k[:4]:round(x*365,2) for k,x in d.items()})
