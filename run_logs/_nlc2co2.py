import sqlite3,sys
db=r"runs\3day_nb_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite"
c=sqlite3.connect(db)
cid=c.execute("select id from entity_class where name='connection'").fetchone()[0]
for (n,) in c.execute("select name from entity where class_id=? and name like '%CO2%' and (name like '%NLC2%')",(cid,)): print(n)
print("-- all NL CO2 conns"); print([n for (n,) in c.execute("select name from entity where class_id=? and name like 'NL%CO2%'",(cid,))])
