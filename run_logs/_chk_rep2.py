import sqlite3,json
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect(db)
    names=[r[0] for r in c.execute("SELECT name FROM parameter_definition WHERE name LIKE '%represent%'")]
    print("==",tag,set(names))
    for p in set(names):
        rs=c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id WHERE pd.name=?""",(p,)).fetchall()
        for n,v in rs:
            try: d=json.loads(v); d=d.get("data",d); print("  ",p,n,"n=",len(d))
            except Exception: print("  ",p,n,v[:50])
    c.close()
