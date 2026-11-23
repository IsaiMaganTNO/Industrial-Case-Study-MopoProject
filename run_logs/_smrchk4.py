import sqlite3
c=sqlite3.connect(r"runs\3day_nb_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite")
cl={n:i for i,n in c.execute("select id,name from entity_class")}
for k in ["node__to_unit","unit__to_node","unit_flow__unit_flow"]:
    print(k,[n for (n,) in c.execute("select name from entity where class_id=? and name like '%REF-SMR-MEA_NLC2%'",(cl[k],))])
