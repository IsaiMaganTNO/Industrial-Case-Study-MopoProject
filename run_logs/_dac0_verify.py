import sqlite3
a=r"runs\3day_mr_ccslow\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow.sqlite"; b=r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_ccslow_dac0.sqlite"
Q="""select e.name, pd.name, al.name, hex(pv.value) from parameter_value pv join entity e on e.id=pv.entity_id
join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative al on al.id=pv.alternative_id"""
A=set(sqlite3.connect(a).execute(Q).fetchall()); B=set(sqlite3.connect(b).execute(Q).fetchall())
print("removed",len(A-B),"added",len(B-A)); print(sorted({(r[1],r[2]) for r in B-A}))
E="select name from entity"; print("entities equal:", set(sqlite3.connect(a).execute(E).fetchall())==set(sqlite3.connect(b).execute(E).fetchall()))
S="select s.name, al.name, sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative al on al.id=sa.alternative_id"
print("scenario equal:", sorted(sqlite3.connect(a).execute(S).fetchall())==sorted(sqlite3.connect(b).execute(S).fetchall()))
