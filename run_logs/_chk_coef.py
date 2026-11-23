import sqlite3,json
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    rs=c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='representative_block_coefficient'""").fetchall()
    tot=0.0
    for n,v in rs:
        try: f=float(v)
        except: f=float("nan")
        tot+=f
    print(tag,"rows",len(rs),"sum=%.6f"%tot)
    for n,v in rs[:4]: print("    ",n,v[:30])
    c.close()
