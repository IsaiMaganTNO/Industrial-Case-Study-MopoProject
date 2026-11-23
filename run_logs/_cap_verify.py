import sqlite3,sys
a=sqlite3.connect(sys.argv[1]);b=sqlite3.connect(sys.argv[2])
for t in ["entity","entity_element","parameter_value","scenario","scenario_alternative","alternative"]:
    A=set(a.execute(f"select * from {t}"));B=set(b.execute(f"select * from {t}"))
    print(t,"removed",len(A-B),"added",len(B-A))
    if t=="parameter_value":
        for r in B-A: print("  changed id",r[0], b.execute("select e.name,a.name from parameter_value pv join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where pv.id=?",(r[0],)).fetchone())
print("methanation atm rows:",b.execute("select count(*) from entity where name like 'methanation%__atmosphere'").fetchone())
