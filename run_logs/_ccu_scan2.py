import sqlite3,sys,collections
con=sqlite3.connect(sys.argv[1]);c=con.cursor()
cls={n:i for i,n in c.execute("select id,name from entity_class")}
atm=set(n.replace("__atmosphere","") for (n,) in c.execute("select name from entity where class_id=? and name like '%__atmosphere'",(cls["unit__to_node"],)))
fam=collections.defaultdict(list)
for (n,) in c.execute("select name from entity where class_id=? and name like 'CO2\\_%' escape '\\'",(cls["node__to_unit"],)):
    u=n.split("__",1)[1]; fam[u.rsplit("_",1)[0]].append(u)
for f,us in sorted(fam.items()):
    u=us[0]
    outs=[x.split("__",1)[1] for (x,) in c.execute("select name from entity where class_id=? and name like ?",(cls["unit__to_node"],u+"\\_\\_%"))] if False else [x.split("__",1)[1] for (x,) in c.execute("select name from entity where class_id=? and substr(name,1,?)=?",(cls["unit__to_node"],len(u)+2,u+"__"))]
    print(f,len(us),"withatm=",sum(x in atm for x in us),"outs(ex)=",outs)
