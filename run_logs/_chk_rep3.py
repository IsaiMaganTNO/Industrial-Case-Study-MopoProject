import sqlite3,json
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect(db)
    for n,v in c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='representative_blocks_by_period'"""):
        d=json.loads(v)["data"]
        k=list(d)[0]; inner=d[k]
        inner=inner.get("data",inner) if isinstance(inner,dict) else inner
        print(tag,n,"outer",len(d),"inner",len(inner))
    c.close()
