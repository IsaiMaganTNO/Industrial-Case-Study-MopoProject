import sqlite3,json
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect(db)
    rs=c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='representative_periods_mapping'""").fetchall()
    print("==",tag,"rows",len(rs))
    for n,v in rs[:6]:
        try: d=json.loads(v)["data"]; print("  ",n,"entries",len(d))
        except Exception as ex: print("  ",n,v[:70])
    c.close()
