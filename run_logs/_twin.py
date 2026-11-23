import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def ex(n):
    return c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection' and e.name=?",(n,)).fetchone()[0]
for a,b in [("BEC1_CH4_BEC2","BEC2_CH4_BEC1"),("BEC1_H2_BEC2","BEC2_H2_BEC1"),
            ("BEC7_CO2_BEC2","BEC2_CO2_BEC7"),("BEC3_CO2_BEC6","BEC6_CO2_BEC3")]:
    print(f"{a:18s}={ex(a)}   {b:18s}={ex(b)}")
