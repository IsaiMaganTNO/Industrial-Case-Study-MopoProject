import sqlite3
c=sqlite3.connect(r"checkpoints\Investment_Results.3day_co2bidir.sqlite")
rows=c.execute("""select e.name,count(*) from entity e join entity_class ec on ec.id=e.class_id
 where ec.name like '%report%' and e.name like '%penalt%' group by 1""").fetchall()
print("penalty report entities:",rows[:5])
# objective terms
for n, in c.execute("select distinct name from entity_class where name like '%objective%' or name like '%penalt%'"):
    print("class:",n)
