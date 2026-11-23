import sqlite3
c=sqlite3.connect(r"runs\3day_nb_ctry_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ctry_ccslow.sqlite")
for (n,) in c.execute("select name from entity where name like 'methanation\\_BEC1%' escape '\\' or name like '%\\_\\_methanation\\_BEC1' escape '\\'"): print(n)
