import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
print("CO2 connections touching BEC6/BEC7:")
n=0
for (x,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='connection' AND (e.name LIKE '%BEC6%' OR e.name LIKE '%BEC7%') AND e.name LIKE '%CO2%'"""):
    print("   ",x); n+=1
print("   count:",n)
print("\nCO2 injectors and their regions:")
for (x,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND e.name LIKE 'CO2-injection%'"""):
    print("   ",x)
