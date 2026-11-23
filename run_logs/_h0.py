import sqlite3, json
r=r"checkpoints\Investment_Results.3day_hcco2.sqlite"
c=sqlite3.connect(r)
q="""SELECT e.name, pv.value FROM parameter_value pv
 JOIN entity e ON e.id=pv.entity_id
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 WHERE pd.name LIKE 'objective_%' OR e.name LIKE '%objective%'"""
for n,v in c.execute(q):
    s=v.decode() if isinstance(v,bytes) else str(v)
    print(f"  {n[:60]:60s} {s[:60]}")
