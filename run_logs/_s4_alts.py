import sqlite3
c=sqlite3.connect(r"share_frlu_xpress\input.sqlite")
q="""select e.name,pd.name,a.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where a.name in ('limited_nuclear-3','limited_fossil-CH4','GA_flex20','high_CO2','medium_CO2') and e.name not like 'CO2-storage%' limit 15"""
for r in c.execute(q): print(r[0][:50],r[1],r[2],r[3][:160])
print(c.execute("select a.name,count(*) from parameter_value pv join alternative a on a.id=pv.alternative_id group by a.name").fetchall())
