import sqlite3
c=sqlite3.connect(r"runs\3day_nb_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite")
print([n for (n,) in c.execute("select name from entity_class")if "node" in n and "unit" in n])
for (n,) in c.execute("select e.name from entity e where e.name like '%REF-SMR-MEA_NLC2%' or e.name like 'HC_NLC2%' or e.name like '%HC_NLC2%' limit 40"): print(n)
