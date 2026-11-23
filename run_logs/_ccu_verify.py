import sqlite3,sys
a=sqlite3.connect(sys.argv[1]);b=sqlite3.connect(sys.argv[2])
for t in ["entity","entity_element","parameter_value","scenario","scenario_alternative","alternative"]:
    A=set(a.execute(f"select * from {t}"));B=set(b.execute(f"select * from {t}"))
    print(t,"removed",len(A-B),"added",len(B-A))
pv=b.execute("select e.name,p.value from parameter_value p join entity e on e.id=p.entity_id where e.name like 'methanation%atmosphere%'").fetchall()
print(len(pv),pv[:2])
