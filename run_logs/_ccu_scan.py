import sqlite3,sys
con=sqlite3.connect(sys.argv[1]);c=con.cursor()
cls={n:i for i,n in c.execute("select id,name from entity_class")}
atm=set(n.replace("__atmosphere","") for (n,) in c.execute("select name from entity where class_id=? and name like '%__atmosphere'",(cls["unit__to_node"],)))
for (u,) in c.execute("select name from entity where class_id=? and (name like '%ethanat%' or name like '%MeOH%' or name like '%FT%') order by name",(cls["unit"],)):
    ins=[x.split("__")[0] for (x,) in c.execute("select name from entity where class_id=? and name like ?",(cls["node__to_unit"],"%__"+u))]
    outs=[x.split("__",1)[1] for (x,) in c.execute("select name from entity where class_id=? and name like ?",(cls["unit__to_node"],u+"__%"))]
    print(u,"atm" if u in atm else "NOATM",ins,outs)
