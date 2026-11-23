import sqlite3
con=sqlite3.connect('checkpoints/Investment_Results.3day_mr_fix.sqlite')
for r in con.execute("select distinct pd.name from parameter_definition pd join parameter_value pv on pv.parameter_definition_id=pd.id"): print(r)
for r in con.execute("select e.name from entity e where e.name like '%CH4%' and (e.name like '%DE%' or e.name like '%UK%') limit 15"): print(r)
