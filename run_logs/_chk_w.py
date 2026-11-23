import sqlite3,json
for tag,db in [("7day",r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"),
               ("3day",r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite")]:
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    print("==",tag)
    for p in ("block_weight","weight","representative_periods_weight"):
        rs=c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id WHERE pd.name=?""",(p,)).fetchall()
        if not rs: continue
        tot=0.0; rep=0.0
        for n,v in rs:
            try: f=float(v)
            except: continue
            tot+=f
            if n.startswith("representative_period"): rep+=f
        print("  %-28s rows=%-4d sum=%.4f repsum=%.4f"%(p,len(rs),tot,rep))
    c.close()
