import sqlite3, json, collections
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
q=c.execute("""
select e.name, ec.name from entity e join entity_class ec on ec.id=e.class_id
where ec.name='connection' and e.name like '%CO2%'
""").fetchall()
print("CO2 connections:",len(q))
for n,_ in q[:50]: print("  ",n)
