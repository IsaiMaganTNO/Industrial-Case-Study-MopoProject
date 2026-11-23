import sqlite3,sys
con=sqlite3.connect(sys.argv[1]);c=con.cursor()
cls={n:i for i,n in c.execute("select id,name from entity_class")}
for pat in ["oil-eng\\_BEC1","oil-boiler-existing\\_BEC1"]:
    print(pat, c.execute("select count(*) from entity where class_id=? and name like ? escape '\\'",(cls["unit__to_node"],pat+"__atmosphere")).fetchone())
print("MeOH consumers:",[n for (n,) in c.execute("select name from entity where class_id=? and name like 'MeOH\\_BEC1%' escape '\\'",(cls["node__to_unit"],))])
print("HC consumers BEC1:",[n for (n,) in c.execute("select name from entity where class_id=? and name like 'HC\\_BEC1%' escape '\\'",(cls["node__to_unit"],))])
