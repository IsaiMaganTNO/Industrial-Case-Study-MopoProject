import sqlite3
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect(db)
    for p in ("storage_investment_count_max_cumulative","storage_state_max"):
        r=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id
          WHERE e.name='atmosphere' AND pd.name=?""",(p,)).fetchall()
        print(tag,p,r)
    c.close()
