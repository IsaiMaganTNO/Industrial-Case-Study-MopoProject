import sqlite3,json
db=r"checkpoints\Investment_Results.3day_hcco2.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name, cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='node_state_longterm' AND e.name LIKE '%atmosphere%'""").fetchall()
print("rows",len(rs))
for n,v in rs:
    try:
        d=json.loads(v)["data"]
        vals=[x[1] for x in d] if isinstance(d,list) else list(d.values())
        fl=[float(x) for x in vals]
        print(n[:60],"n=",len(fl),"min=%.3f max=%.3f"%(min(fl),max(fl)))
    except Exception as ex: print(n[:60],"ERR",str(ex)[:40],v[:60])
c.close()
