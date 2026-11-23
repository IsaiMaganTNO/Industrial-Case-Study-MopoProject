import sqlite3,json,sys
c=sqlite3.connect(sys.argv[1])
cls={n:i for i,n in c.execute("select id,name from entity_class")}
m=[n for (n,) in c.execute("select name from entity where class_id=? and name like 'methanation\\_%' escape '\\'",(cls["unit"],))]
print("methanation units",len(m),m[:3],m[-3:])
print("CH4 links ex:",[n for (n,) in c.execute("select name from entity where class_id=? and name like 'methanation%__CH4%'",(cls["unit__to_node"],))][:4])
print("atm on methanation:",c.execute("select count(*) from entity where name like 'methanation%__atmosphere'").fetchone())
for e,a,v in c.execute("select e.name,a.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name='storage_investment_count_fix_cumulative' and a.name='low_CO2'"):
    print(e,a,{k[:4]:round(x*365,2) for k,x in json.loads(v)["data"].items()})
print(c.execute("select s.name,group_concat(a.name) from scenario s join scenario_alternative sa on sa.scenario_id=s.id join alternative a on a.id=sa.alternative_id group by s.name").fetchall())
print("DAC existing_units:",c.execute("select count(*),min(cast(pv.value as text)) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='existing_units' and e.name like 'DAC\\_%' escape '\\'").fetchone())
